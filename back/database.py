import sqlite3
from passlib.context import CryptContext

DATABASE_URL = "../clinica.db" 

def config_database():
    print("INICIALIZANDO E CONFIGURANDO O BANCO DE DADOS...")
    conexao = sqlite3.connect(DATABASE_URL)
    cursor = conexao.cursor()

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
    
    # Esta verificação impede a criação duplicada do administrador
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
    print("BANCO DE DADOS CONFIGURADO COM SUCESSO!")

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