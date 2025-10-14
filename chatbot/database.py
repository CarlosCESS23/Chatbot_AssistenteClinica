# chatbot/database.py

import sqlite3
from datetime import datetime, timedelta
from .config import logger

DATABASE_URL = "../data/clinica.db"

def get_db_connection():
    """Retorna uma conexão com o banco de dados."""
    conexao = sqlite3.connect(DATABASE_URL)
    conexao.row_factory = sqlite3.Row
    return conexao

def config_database():
    """Cria todas as tabelas necessárias no banco de dados se elas não existirem."""
    print("INICIALIZANDO E CONFIGURANDO O BANCO DE DADOS (CHATBOT)...")
    conexao = get_db_connection()
    cursor = conexao.cursor()
    
    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tabela de Clínicas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Clinicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            zona TEXT NOT NULL
        );
    """)

    # Tabela de Agendamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_clinica INTEGER,
            id_usuario INTEGER,
            data_hora TIMESTAMP NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('disponivel', 'reservado')) DEFAULT 'disponivel',
            FOREIGN KEY (id_clinica) REFERENCES Clinicas (id),
            FOREIGN KEY (id_usuario) REFERENCES Usuarios (id)
        );
    """)
    
    conexao.commit()
    conexao.close()
    print("BANCO DE DADOS CONFIGURADO COM SUCESSO (CHATBOT)!")


def get_or_create_user(telegram_id: int, nome: str) -> None:
    """Busca um usuário pelo ID do Telegram ou o cria se não existir."""
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT id FROM Usuarios WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO Usuarios (telegram_id, nome) VALUES (?, ?)", (telegram_id, nome))
        conexao.commit()
        logger.info(f"Novo usuário criado: {nome} (ID Telegram: {telegram_id})")
    conexao.close()

def bancos_de_dados_ficticios():
    """Popula o banco de dados com clínicas e horários fictícios se estiver vazio."""
    conexao = get_db_connection()
    cursor = conexao.cursor()

    # Verifica se já existem clínicas para não duplicar os dados
    cursor.execute("SELECT COUNT(*) FROM Clinicas")
    if cursor.fetchone()[0] > 0:
        conexao.close()
        logger.info("Banco de dados já populado com dados fictícios.")
        return

    logger.info("Populando o banco de dados com clínicas e agendamentos fictícios...")
    
    # Insere Clínicas Fictícias
    clinicas = [
        ('Clínica Coração de Jesus', 'Norte'), ('Clínica Bem-Estar', 'Norte'),
        ('Clínica Saúde Plena', 'Sul'), ('Clínica Vida Longa', 'Sul'),
        ('Clínica Sorriso', 'Leste'), ('Clínica Visão Clara', 'Leste'),
        ('Clínica OrtoPé', 'Oeste'), ('Clínica DermatoPele', 'Oeste')
    ]
    cursor.executemany("INSERT INTO Clinicas (nome, zona) VALUES (?, ?)", clinicas)
    conexao.commit()

    # Insere Agendamentos Disponíveis Fictícios
    cursor.execute("SELECT id FROM Clinicas")
    clinica_ids = [row[0] for row in cursor.fetchall()]
    agendamentos = []
    
    # Cria horários para os próximos 5 dias
    for clinica_id in clinica_ids:
        for dia in range(1, 6):
            for hora in range(9, 18, 2): # Horários a cada 2 horas
                data_hora = datetime.now().replace(hour=hora, minute=0, second=0, microsecond=0) + timedelta(days=dia)
                agendamentos.append((clinica_id, data_hora.isoformat()))

    cursor.executemany("INSERT INTO Agendamentos (id_clinica, data_hora) VALUES (?, ?)", agendamentos)
    conexao.commit()
    conexao.close()
    logger.info("Dados fictícios inseridos com sucesso!")


def get_user_id(telegram_id: int) -> int | None:
    """Busca o ID do usuário no banco de dados a partir do ID do Telegram."""
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT id FROM Usuarios WHERE telegram_id = ?", (telegram_id,))
    resultado = cursor.fetchone()
    conexao.close()
    return resultado[0] if resultado else None

def get_clinics_by_zone(zona: str) -> list[tuple]:
    """Retorna uma lista de clínicas de uma determinada zona."""
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM Clinicas WHERE zona = ?", (zona,))
    clinicas = cursor.fetchall()
    conexao.close()
    return [(row['id'], row['nome']) for row in clinicas]

def get_avaliable_appointments(id_clinica: int) -> list[tuple]:
    """Retorna horários disponíveis para uma clínica."""
    conexao = get_db_connection()
    cursor = conexao.cursor()
    query = """
        SELECT id, data_hora FROM Agendamentos
        WHERE id_clinica = ? AND status = 'disponivel' AND data_hora > ?
        ORDER BY data_hora LIMIT 5;
    """
    cursor.execute(query, (id_clinica, datetime.now().isoformat()))
    agendamentos = cursor.fetchall()
    conexao.close()
    return [(row['id'], row['data_hora']) for row in agendamentos]

def book_appointment(id_agendamento: int, id_usuario: int) -> bool:
    """Reserva um horário, atualizando o status e associando ao usuário."""
    conexao = get_db_connection()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "UPDATE Agendamentos SET status = 'reservado', id_usuario = ? WHERE id = ? AND status = 'disponivel'",
            (id_usuario, id_agendamento)
        )
        conexao.commit()
        # Verifica se alguma linha foi de fato alterada
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Erro ao agendar horário: {e}")
        return False
    finally:
        conexao.close()

def salvar_sintomas(id_usuario: int, sintomas: list[str]):
    """Salva a lista de sintomas para um usuário no banco de dados."""
    if not sintomas:
        return
    conexao = get_db_connection()
    cursor = conexao.cursor()
    dados_para_inserir = [(id_usuario, sintoma) for sintoma in sintomas]
    try:
        cursor.executemany("INSERT INTO Sintomas (id_usuario, sintoma) VALUES (?, ?)", dados_para_inserir)
        conexao.commit()
        logger.info(f"Sintomas {sintomas} salvos para o usuário ID {id_usuario}.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar sintomas para o usuário ID {id_usuario}: {e}")
    finally:
        conexao.close()