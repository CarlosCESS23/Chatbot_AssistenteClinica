import sqlite3
from datetime import datetime, timedelta


def config_database():
    """"Aqui é a configuração do banco de dados,
    onde ele cria caso o banco e as tabelas não existirem"""

    
    #Criação da conexão com banco de dados de SQLite com nome de clinica.db
    conexao = sqlite3.connect('clinica.db')

    # Criação do cursor para executar comandos SQL
    cursor = conexao.cursor()


    # Criação de tabelas:

    #Tabela de Usuários:

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        nome TEXT,
        historico_sintomas TEXT,
        ultima_interacao DATETIME NOT NULL
    );
    """)
    

    #Tabela de Clinica: 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Clinicas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        rua TEXT,
        bairro TEXT NOT NULL,
        zona TEXT NOT NULL
    );
    """)
    
    #Criação de tabela de agendamento:

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_clinica INTEGER NOT NULL,
        id_usuario INTEGER,
        data_hora DATETIME NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('disponivel', 'reservado')),
        FOREIGN KEY (id_clinica) REFERENCES Clinicas (id),
        FOREIGN KEY (id_usuario) REFERENCES Usuarios (id)
    );
    """)
    
    # Salvando as alterações e fechando a conexão

    conexao.commit()
    conexao.close()

def bancos_de_dados_ficticios():
    """Insere dados fictícios de clícas e vagas para Manaus no banco de dados"""
    
    #Criação da conexão com banco de dados de SQLite com nome de clinica.db
    conexao = sqlite3.connect('clinica.db')
    cursor = conexao.cursor()


    #Limpando dados antigos para não duplicar:
    cursor.execute("DELETE FROM Clinicas;")
    cursor.execute("DELETE FROM Agendamentos;")

    clinicas = [
        (1, 'UBS Dr. Silva', 'Rua das Flores, 123', 'Cidade Nova', 'Norte'),
        (2, 'Clínica Popular Zona Leste', 'Av. Autaz Mirim, 456', 'Jorge Teixeira', 'Leste'),
        (3, 'Centro de Saúde da Compensa', 'Rua da Prata, 789', 'Compensa', 'Oeste'),
        (4, 'Posto de Saúde Petrópolis', 'Av. Beira Rio, 101', 'Petrópolis', 'Sul')
    ]
    
     # 1. Adicionamos a palavra-chave "VALUES"
    # 2. Especificamos os nomes das colunas para mais robustez
    comando_sql = "INSERT INTO Clinicas (id, nome, rua, bairro, zona) VALUES (?, ?, ?, ?, ?);"
    cursor.executemany(comando_sql, clinicas)

    agendamentos = []
    now = datetime.now()
    for id_clinica in range(1, len(clinicas) + 1):
        for dia in range(2):
            for hora in range(8, 12):
                slot_time = datetime(now.year, now.month, now.day, hora, 0, 0) + timedelta(days=dia)
                agendamentos.append((id_clinica, None, slot_time, 'disponivel'))

    comando_sql_agendamentos = "INSERT INTO Agendamentos (id_clinica, id_usuario, data_hora, status) VALUES (?, ?, ?, ?);"
    cursor.executemany(comando_sql_agendamentos, agendamentos)

    conexao.commit()
    conexao.close()
    print("Dados fictícios inseridos com sucesso!")