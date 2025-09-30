import sqlite3
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List
from telegram import Bot
from telegram.ext import Application
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from database import get_db_connection
from models import Consulta,Notificacao


#Carrega as variáveis de ambiente
load_dotenv("../.env")


#Aqui seria as configurações iniciais 
app = FastAPI()

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

@app.get("/consultas",response_model=List[Consulta])
def listar_consultas():
    """
    Aqui ele busca no banco de todas as consultas agendadas e retorna informações
    combinadas do pacientes e da clínica
    """

    conexao = get_db_connection(DATABASE_URL)
    cursor = conexao.cursor()

    #Aqui é onde vai ser o query que vai junta as tabelas de agendamentos, Usuario e cliente

    query = """
        Select 
            a.id as id_agendamento,
            a.data_hora,
            u.nome as nome_paciente,
            u.telegram_id,
            c.nome as nome_clinica,
            c.zona as zona_clinica
        FROM Agendamentos a
        JOIN Usuarios u ON a.id_usuario = u.id
        JOIN Clinicas c ON a.id_clinica = c.id
        WHERE a.status = 'reservado'
        ORDER BY a.data_hora;   
        """
    
    #Convertendo os resultados do banco para o formato domodelo Pydantic
    cursor.execute(query)
    consultas_raw = cursor.fetchall()
    cursor.close()

    #Converte os resultados do banco para o formato do modelo Pydantic
    consultas = [dict(row) for row in consultas_raw]
    return consultas

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
