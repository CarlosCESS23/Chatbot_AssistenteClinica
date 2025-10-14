# back/database.py

import sqlite3
from passlib.context import CryptContext

DATABASE_URL = "/data/clinica.db" 

def config_database():
    print("INICIALIZANDO E CONFIGURANDO O BANCO DE DADOS (BACKEND)...")
    conexao = sqlite3.connect(DATABASE_URL)
    cursor = conexao.cursor()

    # --- TABELA FUNCIONARIOS (sem alterações) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Funcionarios(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nome TEXT NOT NULL,
                   email TEXT UNIQUE NOT NULL,
                   hashed_password TEXT NOT NULL,
                   role TEXT NOT NULL CHECK(role IN ('admin', 'funcionario')),
                   status TEXT NOT NULL CHECK (status IN ('pending', 'active')) DEFAULT 'pending'
        ); 
    """)
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Garante que a tabela Clinicas seja criada exatamente como o chatbot espera,
    # sem a coluna 'bairro'.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Clinicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            zona TEXT NOT NULL
        );
    """)

    # --- As outras tabelas que o chatbot também cria ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Sintomas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            sintoma TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios (id)
        );
    """)
    # --- FIM DA CORREÇÃO ---
    
    # Cria o administrador padrão (sem alterações)
    cursor.execute("SELECT id FROM Funcionarios WHERE role = 'admin' AND email = 'admin@clinica.com'")
    if cursor.fetchone() is None:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin_password_hash = pwd_context.hash("admin123")
        cursor.execute(
            "INSERT INTO Funcionarios (nome, email, hashed_password, role, status) VALUES (?, ?, ?, ?, ?)",
            ("Admin Padrão", "admin@clinica.com", admin_password_hash, "admin", "active")
        )
        print("Administrador padrão criado com sucesso!")
        print("Email: admin@clinica.com | Senha: admin123")
    
    conexao.commit()
    conexao.close()
    print("BANCO DE DADOS CONFIGURADO COM SUCESSO (BACKEND)!")

def get_db_connection():
    conexao = sqlite3.connect(DATABASE_URL)
    conexao.row_factory = sqlite3.Row
    return conexao

def get_funcionario_by_email(email: str):
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM Funcionarios WHERE email = ?", (email,))
    funcionario = cursor.fetchone()
    conexao.close()
    if funcionario: 
        return dict(funcionario)
    return None