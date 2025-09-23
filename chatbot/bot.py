
"""Aqui é onde o bot é configurado e executado, carregando as configurações e inicaliza os modelos
de IA e monta o ConversationHandler com as funções definidas em handlers.py
"""


import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler
)

from .config import logger, model, TELEGRAM_API_KEY as TELEGRAM_BOT_TOKEN
# Importa as funções de resposta e os estados da conversa

from . import handlers
from . import database

def run() -> None:
    """Iniciando o  bot e configurando o COnversationHandler. """

    #Preparando o banco de dados
    database.config_database()
    database.bancos_de_dados_ficticios()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start)],
        states={
            handlers.CHOOSING: [
                CallbackQueryHandler(handlers.prompt_for_symptoms, pattern="^iniciar_consulta$"),
                CallbackQueryHandler(handlers.como_funciona, pattern="^como_funciona$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_instead_of_button),
            ],
            handlers.DESCRIBING_SYMPTOMS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.analyze_symptoms)
            ],
        },
        fallbacks=[CommandHandler('cancelar', handlers.cancelar)],
    )

    application.add_handler(conv_handler)
    print("Bot em execução com estrutura de pasta organizada!!!!!")
    application.run_polling()