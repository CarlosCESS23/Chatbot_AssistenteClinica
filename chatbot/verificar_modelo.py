import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente para pegar sua chave de API
# Certifique-se que existe um arquivo .env na mesma pasta ou na pasta do chatbot
try:
    if os.path.exists('chatbot/.env'):
        load_dotenv('chatbot/.env')
    else:
        load_dotenv()
    
    API_KEY = os.getenv("API_KEY_GEMINI")

    if not API_KEY:
        print("Erro: A variável API_KEY_GEMINI não foi encontrada.")
        print("Verifique se o seu arquivo .env está configurado corretamente.")
    else:
        genai.configure(api_key=API_KEY)

        print("--- Modelos de IA Disponíveis para sua Chave ---")
        
        # Pede à API do Google a lista de modelos
        for model in genai.list_models():
            # Verifica se o modelo suporta o método 'generateContent', que é o que usamos
            if 'generateContent' in model.supported_generation_methods:
                print(f"- {model.name}")
        
        print("\n-------------------------------------------------")
        print("Copie um dos nomes acima e cole no seu arquivo chatbot/config.py")

except Exception as e:
    print(f"Ocorreu um erro ao buscar os modelos: {e}")