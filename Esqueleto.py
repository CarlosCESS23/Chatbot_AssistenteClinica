from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,MessageHandler,filters,ContextTypes
import nltk
import google.generativeai as genai
import os
import Casos.Sintomas as sintomas
import logging



#Configuração do logging para registrar eventos e erros:

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level= logging.INFO
)

logger = logging.getLogger(__name__)



#Configuração da chave API do Gemini e do Chatbot do Telegram

API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")

genai.configure(api_key=API_KEY_GEMINI)

SYSTEM_INSTRUCTION = '...'
# Configuração do modelo Gemini
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction = SYSTEM_INSTRUCTION
)


# Caso a chave da API não foi configurada, levanta um erro
if not API_KEY_GEMINI:
    raise ValueError("A chave API do Gemini não foi encontrada. Por favor, defina a variável de ambiente 'API_KEY_GEMINI'.")



# Chatbot do Telegram:

TELEGRAM_API_KEY = os.getenv("API_KEY_CHATBOT")



# Função para lidar com o comando /start

async def start(
        update,
        context,):
     
     #Aqui enviando a mensagem ded boas vindas

     mensagem_boas_vindas = (
         "Olá!, sou assistente virtual de pré-triagem de saúde."
         "Você pode me descrever que sintomas que está sentindo que te darei uma orientação inicial"
         "**Lembre-se**, Eu não posso diagnosticar doenças ou prescrever remédio, apenas orientação o que pode fazer: "
     )

     await update.message.reply_text(mensagem_boas_vindas,parse_mode="Markdown")

async def handle_message(
          update,
          context
):
    #Aqui é onde processa a mensagem do usuário
    texto_usuario = update.message.text
    chat_id = update.message.chat_id

    await context.bot.send_chat_action(chat_id=chat_id,action = telegram.constants.ChatAction.TYPING)

    try:
        #1. Etapa : Extraindo sintomas com NLTK usando a função criada no outro arquivo
        sintomas_identificado = sintomas.extrair_sintomas(texto_usuario)
        logger.info(f"Sintomas identificados: {chat_id} - {sintomas_identificado}")

        #2. Etapa: Criando o prompt: 
        
        prompt = f"""Você é um assistente de saúde virtual para uma clínica pública. Sua função é realizar uma pré-triagem segura e informativa.

                    Siga estas regras OBRIGATORIAMENTE:
                    1.  **NUNCA DIAGNOSTIQUE:** Não dê nome a doenças (não diga "você está com gripe" ou "pode ser dengue"). Use frases como "sintomas como os seus são comuns em casos de...".
                    2.  **NUNCA PRESCREVA MEDICAMENTOS:** Jamais sugira o nome de um remédio específico, nem mesmo de venda livre como dipirona ou paracetamol. Em vez disso, recomende que o usuário converse com um farmacêutico para alívio dos sintomas ou com um médico.
                    3.  **CLASSIFIQUE O RISCO:** Analise os sintomas e classifique-os em uma de três categorias: 'Baixo Risco', 'Risco Moderado' ou 'Alto Risco/Emergência'.
                    4.  **FORNEÇA ORIENTAÇÕES SEGURAS:**
                        -   Para 'Baixo Risco': Ofereça conselhos de autocuidado geral (hidratação, repouso, alimentação leve).
                        -   Para 'Risco Moderado': Recomende agendar uma consulta na clínica.
                        -   Para 'Alto Risco/Emergência': Instrua o usuário a procurar um pronto-socorro ou ligar para o SAMU (192) imediatamente.
                    5.  **INCLUA UM AVISO LEGAL:** Sempre termine suas respostas com um aviso como: "Lembre-se, sou uma inteligência artificial e minhas orientações não substituem uma consulta médica. Na dúvida, sempre procure um profissional de saúde."
                    6.  **SEJA EMPÁTICO E CLARO:** Use uma linguagem simples, acolhedora e direta.
                    
                    pergunta do usuário: {texto_usuario}

                    Sintomas identificados pelo análise de NLTK: **{sintomas_identificado}**
                    
                    Agora, gere uma resposta de orientação segura, empática e clara, seguindo todas as regras acima
                
                    """
        #Enviando o prompt para o Gemini

        response = model.generate_text(prompt)


        #Aqui envia a resposta para o usuário:

        await update.message.reply_text(response.text,parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Erro ao processar a mensagem do usuário : {chat_id} - {e}")
        await update.message.reply_text("Desculpe, ocorreu um erro ao processar sua mensagem, tente novamente mais tarde.")


def main():
    # Aqui é onde se aplica a iniciação do bot

    aplicacao = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    #Adicionando o handlers para comando:

    aplicacao.add_handler(CommandHandler("start", start))
    aplicacao.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot em execução com NLTK...")
    aplicacao.run_polling()


    #iniciando o bot

    print.run_polling()

if __name__ == "__main__":
    main()


        















#     user_text = update.message.text 


#     #Exemplo de tokenização usando NLTK
#     tokens = nltk.word_tokenize(user_text)

#     if "dor no peito" in user_text.lower():
#         response = "Você mencionou 'dor no peito?' isso pode muito sério, procure um médico imediatamente!"
#     else:
#         #Caso a mensagem não contenha algo sério, responde com o Gemini
        

#         model = genai.GenerativeModel("gemini-1.5-flash") # Aqui é a definição do tipo de modelo
#         
