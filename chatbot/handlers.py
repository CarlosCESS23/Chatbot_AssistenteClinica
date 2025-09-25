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
    """Analisa os sintomas usando a IA com um prompt aprimorado e salva no banco."""
    user = update.message.from_user
    symptoms = update.message.text
    
    # MODIFICAÇÃO 1: Mensagem de espera um pouco mais amigável.
    await update.message.reply_text(
        "Obrigado por compartilhar. Estou analisando suas informações com cuidado... 🤔"
    )

    # MODIFICAÇÃO 2 (A PRINCIPAL): O prompt foi completamente reescrito.
    # Agora ele define uma persona, um tom de voz e a estrutura da resposta.
    prompt = f"""
    **Sua Persona:** Você é um assistente de triagem virtual. Seu tom deve ser calmo, empático, profissional e muito acolhedor. Você NUNCA deve alarmar o paciente.

    **Tarefa:** Analise os sintomas de um paciente e forneça uma resposta amigável e informativa.

    **Sintomas do Paciente:** "{symptoms}"

    **Formato da sua resposta:**
    1.  Comece com uma saudação calorosa, como "Olá! Agradeço por confiar em mim para compartilhar como você está se sentindo."
    2.  Apresente a análise de forma didática, explicando o que os sintomas podem sugerir. Use uma linguagem simples.
    3.  Apresente as sugestões (médico, exames) como recomendações para uma conversa com um profissional de verdade.
    4.  **AVISO OBRIGATÓRIO:** Termine SEMPRE com o seguinte aviso, exatamente como está escrito:
        "**Atenção:** Eu sou uma inteligência artificial e esta análise é uma sugestão baseada nas informações que você forneceu. Ela não substitui uma consulta médica de verdade. Por favor, procure um médico para obter um diagnóstico preciso e um tratamento adequado."
    """
    
    # MODIFICAÇÃO 3: Adicionado tratamento de erros para robustez.
    try:
        logging.info(f"Enviando prompt para a IA para o usuário {user.id}")
        generation_result = model.generate_content(prompt)
        ai_response = generation_result.text

        database.inserir_consulta(user.id, user.first_name, symptoms, ai_response)
        logging.info(f"Consulta salva para o usuário {user.id}")

        await update.message.reply_text(ai_response, reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        logging.error(f"Erro ao processar sintomas para o usuário {user.id}: {e}", exc_info=True)
        await update.message.reply_text(
            "Desculpe, ocorreu um erro ao tentar analisar suas informações. Por favor, tente novamente mais tarde ou use o comando /cancelar."
        )
        return ConversationHandler.END

    # MODIFICAÇÃO 4: Mensagem final de encerramento.
    await update.message.reply_text("Espero ter ajudado! Se cuide. Se precisar de algo mais, pode me chamar com o comando /start.")
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


        