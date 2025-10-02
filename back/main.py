import sqlite3
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler
)
from fastapi import FastAPI, HTTPException, Depends, status, Query
from pydantic import BaseModel
from typing import List, Optional
from telegram import Bot
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager  # <-- 1. Importar o asynccontextmanager

# Importações dos seus módulos locais
from database import get_db_connection, get_funcionario_by_email, config_database
from security import (
    oauth2_scheme, 
    verify_password,  # Corrigido de verify_password
    create_access_token, 
    pwd_context, 
    get_current_active_admin, 
    get_current_active_funcionario
)
from models import Consulta, Notificacao, Token, FuncionarioCreate, Funcionario, Clinica
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='Token')

#Carrega as variáveis de ambiente
load_dotenv("../.env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código a ser executado na inicialização
    print("Iniciando a aplicação e configurando o banco de dados...")
    config_database(DATABASE_URL)
    yield
    # Código a ser executado no desligamento (se necessário)
    print("Aplicação encerrada.")


#Aqui seria as configurações iniciais 
app = FastAPI(lifespan=lifespan)

#Aqui é a configuração de CORS que permite o REACT acesse o back

origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# O Caminho do banco de dados:

DATABASE_URL = "../clinica.db"
TELEGRAM_BOT_TOKEN = os.getenv("API_KEY_CHATBOT")

@app.get("/consultas", response_model=List[Consulta])
def listar_consultas(
    current_user: dict = Depends(get_current_active_funcionario),
    clinica_id: Optional[int] = Query(None, description="Filtra as consultas por ID da clínica")
):
    """
    Lista as consultas. Agora aceita um `clinica_id` opcional para filtrar os resultados.
    """
    conn = get_db_connection(DATABASE_URL)
    cursor = conn.cursor()
    
    # A base da query é a mesma
    base_query = """
    SELECT a.id as id_agendamento, a.data_hora, u.nome as nome_paciente, u.telegram_id, c.nome as nome_clinica, c.zona as zona_clinica
    FROM Agendamentos a
    JOIN Usuarios u ON a.id_usuario = u.id
    JOIN Clinicas c ON a.id_clinica = c.id
    WHERE a.status = 'reservado'
    """
    params = []

    # Se um ID de clínica for fornecido, adicionamos o filtro à query
    if clinica_id:
        base_query += " AND a.id_clinica = ?"
        params.append(clinica_id)
    
    base_query += " ORDER BY a.data_hora;"

    cursor.execute(base_query, params)
    consultas_raw = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in consultas_raw]

@app.post("/notificar")
async def enviar_notificacao(notificacao: Notificacao):
    """
    Recebe um ID do Telegram e uma mensagem, e envia para o usuário
    através do bot
    """

    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(
            status_code = 500,
            detail="Token do Telegram não configurado"
        )
    try:
        #Inicializa apenas o bot para enviar a mensagem:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


        #Montando a mensagem de aviso:

        mensagem_formatada = f"⚠️ **Aviso da Clínica** ⚠️\n\nOlá!\n{notificacao.mensagem}"

        await application.bot.send_message(
            chat_id = notificacao.telegram_id,
            text = mensagem_formatada,
            parse_mode = 'Markdown'
        )
        return {"status": "sucesso","detail":"Mensagem enviada"}
    except Exception as e:

        #Caso o usuário tenha bloqueado o bot ou o ID é inválido:
        print(f"Erro ao enviar notificação: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível enviar a mensagem para o usuário. Erro: {e}"
            )


# ... (Endpoints de /token, /funcionarios/signup, /admin/* permanecem os mesmos)
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_funcionario_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user["status"] != "active":
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/funcionarios/signup")
async def signup_funcionario(funcionario: FuncionarioCreate):
    db_user = get_funcionario_by_email(funcionario.email,DATABASE_URL)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(funcionario.password)
    conn = get_db_connection(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Funcionarios (nome, email, hashed_password, role, status) VALUES (?, ?, ?, ?, ?)",
        (funcionario.nome, funcionario.email, hashed_password, "funcionario", "pending")
    )
    conn.commit()
    conn.close()
    return {"status": "success", "detail": "Registration request sent, waiting for admin approval."}

@app.get("/admin/funcionarios", response_model=List[Funcionario])
async def get_all_funcionarios(current_admin: dict = Depends(get_current_active_admin)):
    conn = get_db_connection(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, role, status FROM Funcionarios")
    funcionarios_raw = cursor.fetchall()
    conn.close()
    return [dict(row) for row in funcionarios_raw]

@app.post("/admin/aprovar/{funcionario_id}")
async def approve_funcionario(funcionario_id: int, current_admin: dict = Depends(get_current_active_admin)):
    conn = get_db_connection(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("UPDATE Funcionarios SET status = 'active' WHERE id = ?", (funcionario_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "detail": f"Funcionario {funcionario_id} approved."}

@app.delete("/admin/remover/{funcionario_id}")
async def remove_funcionario(funcionario_id: int, current_admin: dict = Depends(get_current_active_admin)):
    conn = get_db_connection(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Funcionarios WHERE id = ?", (funcionario_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "detail": f"Funcionario {funcionario_id} removed."}

@app.get("/clinicas", response_model=List[Clinica])
def listar_clinicas(current_user: dict = Depends(get_current_active_funcionario)):
    """Fornece uma lista de todas as clínicas para o frontend."""
    conn = get_db_connection(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, zona FROM Clinicas")
    clinicas_raw = cursor.fetchall()
    conn.close()
    return [dict(row) for row in clinicas_raw]


