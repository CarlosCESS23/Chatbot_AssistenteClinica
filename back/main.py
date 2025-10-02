import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status, Query
from typing import List, Optional
from telegram import Bot
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from database import get_db_connection, get_funcionario_by_email, config_database
from security import verify_password, create_access_token, get_current_active_admin, get_current_active_funcionario
from models import Consulta, Notificacao, Token, FuncionarioCreate, Funcionario, Clinica
from fastapi.security import OAuth2PasswordRequestForm

load_dotenv("../.env")
DATABASE_URL = "../clinica.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    config_database()
    yield

app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000", "http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TELEGRAM_BOT_TOKEN = os.getenv("API_KEY_CHATBOT")

# ENDPOINTS DE AUTENTICAÇÃO E CADASTRO
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_funcionario_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")
    if user["status"] != "active":
        raise HTTPException(status_code=400, detail="Utilizador inativo ou pendente de aprovação")

    # --- ALTERAÇÃO AQUI ---
    # Adicionamos 'role' e 'nome' ao payload do token.
    access_token_data = {
        "sub": user["email"],
        "role": user["role"],
        "name": user["nome"]
    }
    access_token = create_access_token(data=access_token_data)
    # --- FIM DA ALTERAÇÃO ---

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/funcionarios/signup", response_model=Funcionario)
async def signup_funcionario(funcionario: FuncionarioCreate):
    db_user = get_funcionario_by_email(funcionario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registado")
    
    from security import get_password_hash
    hashed_password = get_password_hash(funcionario.password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Funcionarios (nome, email, hashed_password, role, status) VALUES (?, ?, ?, ?, ?)",
        (funcionario.nome, funcionario.email, hashed_password, "funcionario", "pending")
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id, **funcionario.dict(exclude={"password"}), "role": "funcionario", "status": "pending"}

# ENDPOINTS DE ADMINISTRAÇÃO
@app.get("/admin/funcionarios", response_model=List[Funcionario])
async def get_all_funcionarios(current_admin: dict = Depends(get_current_active_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, role, status FROM Funcionarios")
    funcionarios_raw = cursor.fetchall()
    conn.close()
    return [dict(row) for row in funcionarios_raw]

@app.post("/admin/aprovar/{funcionario_id}", response_model=Funcionario)
async def approve_funcionario(funcionario_id: int, current_admin: dict = Depends(get_current_active_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Atualizar o status do funcionário
    cursor.execute("UPDATE Funcionarios SET status = 'active' WHERE id = ?", (funcionario_id,))
    conn.commit()

    # 2. Verificar se a atualização foi bem-sucedida
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    # 3. Buscar os dados completos do funcionário recém-aprovado
    cursor.execute("SELECT id, nome, email, role, status FROM Funcionarios WHERE id = ?", (funcionario_id,))
    funcionario_aprovado = cursor.fetchone()
    conn.close()

    # 4. Devolver o objeto completo, que corresponde ao response_model
    return dict(funcionario_aprovado)

@app.delete("/admin/remover/{funcionario_id}")
async def remove_funcionario(funcionario_id: int, current_admin: dict = Depends(get_current_active_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Funcionarios WHERE id = ?", (funcionario_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# ENDPOINTS PARA FUNCIONÁRIOS
@app.get("/clinicas", response_model=List[Clinica])
def listar_clinicas(current_user: dict = Depends(get_current_active_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, zona FROM Clinicas")
    clinicas_raw = cursor.fetchall()
    conn.close()
    return [dict(row) for row in clinicas_raw]

@app.get("/consultas", response_model=List[Consulta])
def listar_consultas(
    current_user: dict = Depends(get_current_active_funcionario),
    clinica_id: Optional[int] = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    base_query = "SELECT a.id as id_agendamento, a.data_hora, u.nome as nome_paciente, u.telegram_id, c.nome as nome_clinica, c.zona as zona_clinica FROM Agendamentos a JOIN Usuarios u ON a.id_usuario = u.id JOIN Clinicas c ON a.id_clinica = c.id WHERE a.status = 'reservado'"
    params = []
    if clinica_id:
        base_query += " AND a.id_clinica = ?"
        params.append(clinica_id)
    base_query += " ORDER BY a.data_hora;"
    cursor.execute(base_query, params)
    consultas_raw = cursor.fetchall()
    conn.close()
    return [dict(row) for row in consultas_raw]

@app.post("/notificar")
async def enviar_notificacao(notificacao: Notificacao, current_user: dict = Depends(get_current_active_funcionario)):
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Token do Telegram não configurado.")
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        mensagem_formatada = f"⚠️ *Aviso da Clínica*\n\nOlá!\n{notificacao.mensagem}"
        await bot.send_message(chat_id=notificacao.telegram_id, text=mensagem_formatada, parse_mode='Markdown')
        return {"status": "sucesso"}
    except Exception as e:
        detail = f"Não foi possível enviar a mensagem. Erro: {e}"
        if "Chat not found" in str(e):
            detail = "Não foi possível enviar a mensagem. O utilizador pode ter bloqueado o bot."
        raise HTTPException(status_code=400, detail=detail)