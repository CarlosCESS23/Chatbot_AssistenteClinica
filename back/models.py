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

#Criação do model de Funcionário
class Funcionario(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    status: str

#Verificação de token, quando foi acessado e o tipo
class Token(BaseModel):
    access_token: str
    token_type : str

class FuncionarioCreate(BaseModel):
    nome: str
    email: str
    password: str


class Consulta(BaseModel):
    id_agendamento: int
    data_hora: str
    nome_paciente: str
    telegram_id: int
    nome_clinica: str
    zona_clinica: str

class Clinica(BaseModel):
    id: int
    nome: str
    zona: str