# Funções de bancos de dados:

import sqlite3


def get_db_connection(DATABASE_URL : str):
    """Aqui cria e retorna uma conexão com banco de dados"""
    conexao = sqlite3.connect(DATABASE_URL)
    conexao.row_factory = sqlite3.Row # Isso permite acessar colunas por nome
    return conexao


