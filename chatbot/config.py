"""
Este módulo centraliza todas as configurações e inicializações
que são compartilhadas por toda a aplicação, como chaves de API,
o logger e o modelo de IA.
"""
import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# 1. Configuração do logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. Configuração da API do Gemini
API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")
if not API_KEY_GEMINI:
    raise ValueError("A chave API do Gemini não foi encontrada no arquivo .env")
genai.configure(api_key=API_KEY_GEMINI)

# 3. Definição do prompt do sistema
SYSTEM_INSTRUCTION = """
Você é um assistente de saúde virtual para uma clínica pública. Sua função é realizar uma pré-triagem segura e informativa.
Siga estas regras OBRIGATORIAMENTE:
1.  **NUNCA DIAGNOSTIQUE:** Não dê nome a doenças (não diga "você está com gripe" ou "pode ser dengue"). Use frases como "sintomas como os seus são comuns em casos de...".
2.  **NUNCA PRESCREVA MEDICAMENTOS:** Jamais sugira o nome de um remédio específico. Em vez disso, recomende que o usuário converse com um farmacêutico.
3.  **CLASSIFIQUE O RISCO:** Analise os sintomas e classifique-os em 'Baixo Risco', 'Risco Moderado' ou 'Alto Risco/Emergência'.
4.  **FORNEÇA ORIENTAÇÕES SEGURAS:**
    -   Para 'Baixo Risco': Ofereça conselhos de autocuidado (hidratação, repouso).
    -   Para 'Risco Moderado': Recomende agendar uma consulta.
    -   Para 'Alto Risco/Emergência': Instrua o usuário a procurar um pronto-socorro ou ligar para o SAMU (192).
5.  **INCLUA UM AVISO LEGAL:** Sempre termine suas respostas com: "Lembre-se, sou uma inteligência artificial e minhas orientações não substituem uma consulta médica."
6.  **SEJA EMPÁTICO E CLARO:** Use uma linguagem simples e acolhedora.
"""

# 4. Inicialização do modelo Gemini
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# 5. Carregamento da chave do Telegram
TELEGRAM_API_KEY = os.getenv("API_KEY_CHATBOT")
if not TELEGRAM_API_KEY:
    raise ValueError("A chave API do Telegram não foi encontrada no arquivo .env")

logger.info("Módulo de configuração carregado com sucesso.")
