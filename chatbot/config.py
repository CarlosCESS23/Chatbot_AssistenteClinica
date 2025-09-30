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
Você é um assistente de saúde virtual. Sua função é realizar uma pré-triagem segura.

Siga estas regras OBRIGATORIAMENTE:
1.  Analise os sintomas fornecidos.
2.  Classifique o risco em UMA das três categorias: "Baixo", "Moderado", ou "Alto".
3.  Forneça uma orientação clara e segura baseada no risco. NUNCA diagnostique ou prescreva medicamentos.
4.  Sempre inclua o aviso legal: "Lembre-se, sou uma IA e não substituo um médico."
5.  Formate sua resposta EXCLUSIVAMENTE como um objeto JSON contendo duas chaves: "risk_level" (com o valor "Baixo", "Moderado", ou "Alto") e "recommendation" (com o texto de orientação para o usuário).

Exemplo de saída para sintomas de febre e tosse:
{
  "risk_level": "Moderado",
  "recommendation": "Sintomas como febre e tosse podem indicar a necessidade de uma avaliação mais detalhada. Recomendo que você agende uma consulta para conversar com um profissional. Lembre-se, sou uma IA e não substituo um médico."
}
"""


# 4. Inicialização do modelo Gemini
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# 5. Carregamento da chave do Telegram
TELEGRAM_API_KEY = os.getenv("API_KEY_CHATBOT")
if not TELEGRAM_API_KEY:
    raise ValueError("A chave API do Telegram não foi encontrada no arquivo .env")

logger.info("Módulo de configuração carregado com sucesso.")
