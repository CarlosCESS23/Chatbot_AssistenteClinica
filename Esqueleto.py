import telegram
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup)
from telegram.ext import (
    Application, # Mudei de ApplicationBuilder para Application para simplificar
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler)

import google.generativeai as genai
import os
import Casos.Sintomas as sintomas
import logging
from dotenv import load_dotenv


# Definindo os estados de conversas que vão ser utilizado no futuro:
CHOOSING, DESCRIBING_SYMPTOMS = range(2)

# Carregando o arquivo .env para pegar as chaves da API
load_dotenv()


# Configuração do logging para registrar eventos e erros:
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level= logging.INFO
)
logger = logging.getLogger(__name__)


# Configuração da chave API do Gemini
API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")
# Caso a chave da API não foi configurada, levanta um erro
if not API_KEY_GEMINI:
    raise ValueError("A chave API do Gemini não foi encontrada. Por favor, defina a variável de ambiente 'API_KEY_GEMINI'.")

genai.configure(api_key=API_KEY_GEMINI)

# Definimos o prompt uma vez aqui para ser reutilizado
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

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction = SYSTEM_INSTRUCTION
)

# Chatbot do Telegram:
TELEGRAM_API_KEY = os.getenv("API_KEY_CHATBOT")


# PASSO 1: Usuário envia /start.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa e mostra o menu de botões."""
    teclado = [
        [InlineKeyboardButton("🩺 Iniciar Consulta Básica", callback_data='iniciar_consulta')],
        [InlineKeyboardButton("❓ Como funciona?", callback_data='como_funciona')],
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    mensagem_boas_vindas = "Olá!, eu sou seu assistente virtual de saúde 🤖🩺.\n\nSelecione uma das opções abaixo para começar: "
    await update.message.reply_text(mensagem_boas_vindas, reply_markup=reply_markup)
    return CHOOSING

# PASSO 2: Usuário clica no botão "Iniciar Consulta". Esta função é chamada.
async def prompt_for_symptoms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Responde ao clique do botão e pede ao usuário para descrever os sintomas."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(text="Entendido. Por favor, descreva em uma única mensagem todos os sintomas que você está sentindo.")
    
    # Avança o estado da conversa para esperar pelo texto
    return DESCRIBING_SYMPTOMS

# PASSO 3: Usuário digita os sintomas. Esta função é chamada.
async def analyze_symptoms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a MENSAGEM DE TEXTO com os sintomas do usuário."""
    texto_usuario = update.message.text
    chat_id = update.message.chat_id

    await context.bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.TYPING)

    try:
        sintomas_identificado = sintomas.extrair_sintomas(texto_usuario)
        logger.info(f"Sintomas identificados: {chat_id} - {sintomas_identificado}")

        prompt_final = f"""
        pergunta do usuário: {texto_usuario}
        Sintomas identificados pelo análise de NLTK: **{sintomas_identificado}**
        Agora, gere uma resposta de orientação seguindo as regras do sistema.
        """
        response = model.generate_content(prompt_final)
        await update.message.reply_text(response.text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Erro ao processar a mensagem do usuário : {chat_id} - {e}")
        await update.message.reply_text("Desculpe, ocorreu um erro ao processar sua mensagem, tente novamente mais tarde.")

    await update.message.reply_text("Se precisar de mais alguma coisa, digite /start para ver as opções novamente. 😊")
    return ConversationHandler.END


async def como_funciona(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     """Explica o funcionamento do bot quando o botão correspondente é clicado."""
     query = update.callback_query
     await query.answer()
     mensagem = (
          "É simples! Siga os passos:\n\n"
        "1️⃣ **Clique em 'Iniciar Consulta Básica'** para começar.\n\n"
        "2️⃣ **Descreva seus sintomas** quando eu pedir.\n\n"
        "3️⃣ **Receba a Orientação:** Vou te responder com recomendações seguras.\n\n"
        "**Lembre-se:** Não substituo um médico. Para começar de novo, digite /start."
     )
     await query.edit_message_text(mensagem)
     return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela e sai da conversa."""
    await update.message.reply_text('Operação cancelada. Se precisar de algo, digite /start. 😊')
    return ConversationHandler.END


async def text_instead_of_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Informa ao usuário que ele deve usar os botões."""
    await update.message.reply_text("Por favor, selecione uma das opções nos botões acima para continuar.")


def main() -> None:
    """Inicia o bot e configura o ConversationHandler."""
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                # Quando o botão 'iniciar_consulta' é clicado, chama a função de PROMPT
                CallbackQueryHandler(prompt_for_symptoms, pattern="^iniciar_consulta$"),
                CallbackQueryHandler(como_funciona, pattern="^como_funciona$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, text_instead_of_button),
            ],
            DESCRIBING_SYMPTOMS: [
                # Quando o texto é digitado, chama a função de ANÁLISE
                MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_symptoms)
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    application.add_handler(conv_handler)
    print("Bot em execução com fluxo de conversa...")
    application.run_polling()


if __name__ == "__main__":
    main()

