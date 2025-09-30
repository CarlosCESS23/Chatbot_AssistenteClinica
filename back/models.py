#Isso  ajuda a validar e formatar  os dados da API

import sqlite3
from pydantic import BaseModel


class Consulta(BaseModel):
    id_agendamento: int
    data_hora: str
    nome_paciente: str
    telegram_id: int
    nome_clinica: str
    zona_clinica: str

class Notificacao(BaseModel):
    telegram_id: int
    mensagem: str
