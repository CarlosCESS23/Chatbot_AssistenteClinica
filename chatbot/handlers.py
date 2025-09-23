"""
Aqui nesse módulo contém todas as funções de callback 
(handlers) que respondem às interações do usuário no Telegram.

Cada função é responsável por uma etapa específica do fluxo de conversa do bot.

"""

from telegram import Update, InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import ContextTypes,ConversationHandler
import telegram.constants


#Importando os objetos e funções de outros módulos do pacote

from . import nlp as sintomas
from .config import model,logger


# Definido os estados da conversa para serem usados aqui e no bot.py
CHOOSING, DESCRIBING_SYMPTOMS = range(2)


# PASSO 1: Onde o usuário escrever o /start, esssa função é chamada

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa e mostra o menu de botões."""

    teclado = [
        InlineKeyboardButton("🩺 Iniciar Consulta Básica", callback_data='iniciar_consulta'),
        InlineKeyboardButton("❓ Como funciona?", callback_data='como_funciona')
    ]
    reply_markup = InlineKeyboardMarkup.from_column(teclado)
    mensagem_boas_vindas = "Olá, eu sou seu assistente virtual de saúde 🤖🩺. \n\nSelecione alguma dessas opções abaixo para começar:"
    await update.message.reply_text(mensagem_boas_vindas, reply_markup=reply_markup)

    return CHOOSING

# PASSO 2: Usuário clica no botão de "IniciarConsulta"

async def prompt_for_symptoms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """""Responde ao clique do botão e isso pede ao usuário escrever os sintomas que sente"""
    query = update.callback_query
    await query.answer()


# Aqui edita a mensagem do botão para pedir os sintomas
    await query.edit_message_text(text="Entendido.\n\nPor favor, descreva quais são os sintomas que você sente nesse momento.")
    
    return DESCRIBING_SYMPTOMS


# Passo 3: Usuário digita os sintomas, e após disso a função é chamada

async def analyze_symptoms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Isso processa a MENSAGEM DE TEXTO com os sintomas do usuário
    texto_usuario = update.message.text
    chat_id = update.message.chat_id


    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    
    try:
        sintomas_identificado = sintomas.extrair_sintomas(update.message.text)
        logger.info(f'Sintomas identificados: {update.message.chat_id} - {sintomas_identificado}')
        prompt_for_symptoms = f"""


        pergunta do usuário: {texto_usuario}
        Sintomas identificados pelo análise de NLTK: **{sintomas_identificado}**

        Agora, gere uma resposta de orientação segindo as regras do sistema.
        """
        reponse = model.generate_content(prompt_for_symptoms)

        await update.message.reply_text(reponse.text,parse_mode="Markdown")

    except Exception as e:
        logger.error(f'Erro ao processar a mensagem do usuário {chat_id} - {e}')
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
            "2️⃣ **Descreva seus sintomas** em uma única mensagem.\n\n"
            "3️⃣ **Receba orientações básicas** sobre cuidados iniciais e quando procurar um médico.\n\n"
            "⚠️ **Lembre-se:** Este bot não substitui uma consulta médica profissional. Em casos de emergência, procure ajuda médica imediatamente.\n\n"
            "Se estiver pronto, clique em 'Iniciar Consulta Básica' para começar!"
        )
        await query.edit_message_text(text=mensagem, parse_mode="Markdown")
        return CHOOSING

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     """Cancela e sai da conversa."""
     await update.message.reply_text('Operação cancelada. Se precisar de algo, digite /start')
     return ConversationHandler.END

async def text_instead_of_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Informa o usuário para clicar nos botões em vez de digitar."""
    await update.message.reply_text("Por favor, utilize os botões abaixo para navegar. Digite /start para ver as opções novamente.")
    return CHOOSING


        