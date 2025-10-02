# Funções de bancos de dados:

import sqlite3


def config_database(DATABASE_URL : str):

    print("BANCO DE DADOS INICIALIZADO!!!!!!!!!!!!!!!!!!!")
    
    #Criação de table de funcionário e Admin

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
    
    #Adicionando o adminsitrador padrão:

    cursor.execute(
        "Select id FROM Funcionarios WHERE role = 'admin'"
                   )
    if cursor.fetchone() is None:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin_passow_hash = pwd_context.hash("admin123")

        cursor.execute(
            "INSERT INTO Funcionarios (nome,email,hashed_password,role,status)VALUES (?,?,?,?,?)",
            ("Admin Padrão", "admin@clinica.com",admin_passow_hash,"admin","active")
        )
        print("Administrador padrão criado com sucesso!")
        print("Emai: admin@clinica.com")
        print("Senha: admin123")


#Funções do banco de dados
def get_db_connection(DATABASE_URL : str):
    """Aqui cria e retorna uma conexão com banco de dados"""
    conexao = sqlite3.connect(DATABASE_URL)
    conexao.row_factory = sqlite3.Row # Isso permite acessar colunas por nome
    return conexao

def get_funcionario_by_email(email : str, DATABASE_URL : str):
    conexao = sqlite3.connect(DATABASE_URL)
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM Funcionarios WHERE email = ?",(email,))
    funcionario = cursor.fetchone()
    conexao.close()
    if funcionario: 
        return dict(funcionario)
    return None

