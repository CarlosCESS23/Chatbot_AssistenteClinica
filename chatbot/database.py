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




def get_or_create_user(telegram_id: int, nome: str):
    """
    Verifica se um usuário existe pelo telegram_id.
    - Se existir, atualiza o nome (caso tenha mudado) e a data da última interação.
    - Se não existir, cria um novo registro para esse usuário.
    """
    conexao = sqlite3.connect('clinica.db')
    cursor = conexao.cursor()
    
    # Momento atual, para evitar chamadas repetidas
    now = datetime.now()

    # 1. Tenta buscar o usuário pelo seu ID único do Telegram
    # A sintaxe correta do SELECT é: SELECT colunas FROM tabela WHERE condição
    cursor.execute("SELECT id FROM Usuarios WHERE telegram_id = ?", (telegram_id,))
    user_data = cursor.fetchone() # Pega o primeiro resultado (que deve ser o único)

    if user_data:
        # 2. Se o usuário FOI encontrado, atualiza seus dados
        user_id = user_data[0] # Pega o ID interno do banco
        
        # O comando UPDATE é o correto para modificar um registro existente
        cursor.execute(
            "UPDATE Usuarios SET nome = ?, ultima_interacao = ? WHERE id = ?",
            (nome, now, user_id)
        )
        print(f"Usuário {telegram_id} ({nome}) atualizado no banco de dados.")
    else:
        # 3. Se o usuário NÃO FOI encontrado, cria um novo
        # O comando INSERT é o correto para adicionar um novo registro
        cursor.execute(
            "INSERT INTO Usuarios (telegram_id, nome, ultima_interacao) VALUES (?, ?, ?)",
            (telegram_id, nome, now)
        )
        print(f"Novo usuário {telegram_id} ({nome}) criado no banco de dados.")
        
    # Salva (commit) as alterações no banco de dados
    conexao.commit()
    
    # Fecha a conexão para liberar os recursos
    conexao.close()


def get_clinics_by_zone(zona):
   """Função para retornar uma lista de clínicas de uma determinada zona."""
   conexao = sqlite3.connect('clinica.db')
   cursor = conexao.cursor()
   cursor.execute("Select id, nome from Clinicas Where zona = ?",(zona))
   clinicas = cursor.fetchall()
   conexao.close()
   return clinicas




def get_avaliable_appointments(id_clinica):
   """Função para retornar uma lista de horário disponiveis"""


   conexao = sqlite3.connect('clinica.db')


   cursor = conexao.cursor()


   #Buscando horário para as pŕoximas 48 horas que estão disponíveis
   query_time_limit = datetime.now() + timedelta(hours=48)
   cursor.execute("""
                  Select id,data_hora from Agendamentos
                  Where id_cllinica = ? AND status = 'disponivel' AND data_hora < ?
                  Order by data_hora limit 10
                  """,(id_clinica,query_time_limit))
  
   agendamentos = cursor.fetchall()
   conexao.close()
   return agendamentos
  
def book_appointment(id_agendamento,id_usuario):
   """Uma função para reservar um horário de atendimento para o usuário"""


   #Conexão com banco de dados
   conexao = sqlite3.connect('clinica.db')
   cursor = conexao.cursor()


   try:
       cursor.execute("""
                      Update Agendamentos set id_usuario = ?,status = 'reservado'
                      Where id = ? AND status = 'disponivel'""",(id_usuario,id_agendamento)
                      )
       conexao.commit()


       #Verifica se alguma linha foi alterado, isso confirma se o agendamento foi atualizado
       return cursor.rowcount > 0
   except sqlite3.Error as e:
       print(f"Erro ao reservar o agendamento: {e}")
       return False
   finally:
       conexao.close()


def get_user_id(ID_telegram):
   """Essa função busca o id do usuário no banco a partir do ID do telegram"""


   #Conexão com banco de dados


   conexao = sqlite3.connect('clinica.db')
   cursor = conexao.cursor()


   #Comandos SQL para buscar os agendamentos do usuário
   cursor.execute("select ID from usuario where telegram_id = ?",(ID_telegram))


   resultado = cursor.fetchone()


   conexao.close()


   return resultado[0] if resultado else None
