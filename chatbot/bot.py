"""Aqui é onde o bot é configurado e executado, carregando as configurações e inicaliza os modelos
de IA e monta o ConversationHandler com as funções definidas em handlers.py
"""
from telegram.ext import (
   Application,
   CommandHandler,
   MessageHandler,
   filters,
   CallbackQueryHandler,
   ConversationHandler
)

from .config import logger, TELEGRAM_API_KEY
from . import handlers
from . import database

def run() -> None:
   """Iniciando o  bot e configurando o COnversationHandler. """
   database.config_database()
   database.bancos_de_dados_ficticios()

   application = Application.builder().token(TELEGRAM_API_KEY).build()

   conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start)],
        states={
            handlers.CHOOSING: [
                CallbackQueryHandler(handlers.iniciar_consulta, pattern="^iniciar_consulta$"),
                CallbackQueryHandler(handlers.como_funciona, pattern="^como_funciona$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_instead_of_button),
            ],
            handlers.DESCRIBING_SYMPTOMS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.analyze_symptoms)
            ],
            # CORREÇÃO: Usando o nome correto do estado
            handlers.CHOOSING_CLINIC: [
                CallbackQueryHandler(handlers.show_clinics, pattern="^zona_")
            ],
            handlers.CHOOSING_APPOINTMENT: [
                CallbackQueryHandler(handlers.show_appointments, pattern="^clinica_"),
                CallbackQueryHandler(handlers.book_appointment_callback, pattern="^ag_")
            ]
        },
        fallbacks=[CommandHandler('cancelar', handlers.cancelar)],
    )

   application.add_handler(conv_handler)
   print("Bot em execução com integração ao banco de dados e agendamento!")
   application.run_polling()