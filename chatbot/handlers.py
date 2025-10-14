"""
Aqui nesse módulo contém todas as funções de callback
(handlers) que respondem às interações do usuário no Telegram.


Cada função é responsável por uma etapa específica do fluxo de conversa do bot.


"""



import json 
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import ContextTypes,ConversationHandler
import telegram.constants




#Importando os objetos e funções de outros módulos do pacote


from . import nlp as sintomas
from .config import model,logger, SYSTEM_INSTRUCTION
from . import database




#Aqui define os estados da conversa
CHOOSING, DESCRIBING_SYMPTOMS, ASKING_ZONE, CHOOSING_CLINIC, CHOOSING_APPOINTMENT = range(5)






# Passo 1; Onde o usuário escreve o /start, é chamado aqui
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa, registra o usuário e mostra o menu de botões."""
    user = update.message.from_user
    
    # Garante que o usuário exista no banco de dados
    database.get_or_create_user(user.id, user.first_name)
    logger.info(f"Usuário {user.id} ({user.first_name}) iniciou o bot.")

    # --- CORREÇÃO APLICADA AQUI ---
    # Criamos o teclado como uma lista de listas.
    # Cada lista interna é uma linha de botões.
    teclado = [
        [InlineKeyboardButton("🩺 Iniciar Consulta Básica", callback_data='iniciar_consulta')],
        [InlineKeyboardButton("❓ Como funciona?", callback_data='como_funciona')]
    ]
    
    # Passamos a lista de listas diretamente para o InlineKeyboardMarkup
    reply_markup = InlineKeyboardMarkup(teclado)
    
    mensagem_boas_vindas = f"Olá, {user.first_name}! Eu sou seu assistente virtual de saúde 🤖🩺. \n\nSelecione uma das opções abaixo para começar:"
    
    await update.message.reply_text(mensagem_boas_vindas, reply_markup=reply_markup)

    return CHOOSING


# Passo 2: Onde o usuário escolhe iniciar a consulta:


async def iniciar_consulta(update: Update,
                          context: ContextTypes.DEFAULT_TYPE
                          ) -> int:
   """
   Essa função responde no momento que o usuário clica no botão "Iniciar Consulta Básica",
   pede ao usuário descrever o sintoma
   """
   query = update.callback_query
   await query.answer()
   await query.edit_message_text(
       text= "Entendido,\n\nPor favor, descreva que tipo de sintoma que você está sentido"
   )
   return DESCRIBING_SYMPTOMS


# Passo 3: Onde o usuário digita os sintomas, a função é chamada para efetuar:


async def analyze_symptoms(update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a mensagem de texto, obtém uma resposta JSON da IA e age de acordo."""
    texto_usuario = update.message.text
    chat_id = update.message.chat_id
    user_id_telegram = update.message.from_user.id # Adicionar esta linha

    await context.bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.TYPING)

    try:
        sintomas_identificado = sintomas.extrair_sintomas(texto_usuario)
        logger.info(f'Sintomas identificados para {chat_id}: {sintomas_identificado}')

        id_usuario_db = database.get_user_id(user_id_telegram)
        if id_usuario_db:
            database.salvar_sintomas(id_usuario_db, sintomas_identificado)
            
        prompt_para_ia = f"""

        Analise os seguintes sintomas e gere uma resposta JSON conforme as regras do sistema.

        Sintomas descritos pelo usuário: "{texto_usuario}"
        Sintomas-chave extraídos: {sintomas_identificado}
        """

        

        response = model.generate_content(prompt_para_ia)
        
        # Limpa a resposta da IA para garantir que seja um JSON válido
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        
        try:
            data = json.loads(cleaned_response)
            risk_level = data.get("risk_level", "").lower()
            recommendation = data.get("recommendation", "Não foi possível processar a recomendação.")
        except json.JSONDecodeError:
            logger.error(f"Falha ao decodificar JSON da IA: {response.text}")
            await update.message.reply_text("Desculpe, não consegui processar a resposta da análise. Por favor, tente novamente.")
            return ConversationHandler.END

        # Envia a recomendação de texto para o usuário
        await update.message.reply_text(recommendation, parse_mode="Markdown")

        # Inicia o fluxo de agendamento se o risco for "moderado"
        if risk_level == "moderado":
            return await ask_for_zone(update, context)

        await update.message.reply_text("Se precisar de mais alguma coisa, digite /start para ver as opções novamente. 😊")
        return ConversationHandler.END

    except Exception as e:
        logger.error(f'Erro ao processar a mensagem do usuário {chat_id} - {e}')
        await update.message.reply_text("Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente mais tarde.")
        return ConversationHandler.END
  
   # Passo 4: Perguntar a zona do usuário para sugerir clínicas próximas ( para os casos médios)


async def ask_for_zone(update: Update, 
                       context: ContextTypes.DEFAULT_TYPE) -> int:
    
    """Pergunta ao usuário em qual zona ele reside."""
    # O callback_data agora corresponde ao padrão esperado ("zona_...")
    teclado = [
        [InlineKeyboardButton("Norte", callback_data='zona_Norte'), InlineKeyboardButton("Sul", callback_data='zona_Sul')],
        [InlineKeyboardButton("Leste", callback_data='zona_Leste'), InlineKeyboardButton("Oeste", callback_data='zona_Oeste')]
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    await update.message.reply_text("Para facilitar, posso verificar as clínicas próximas. Em qual zona de Manaus você está?", reply_markup=reply_markup)
    return CHOOSING_CLINIC




# Passo 5 : Mostra as clínicas da zona escolhida


async def show_clinics(update: Update,
                      context: ContextTypes.DEFAULT_TYPE
                      ) -> int:
    """
    Isso mostra as clínicas da zona escolhida pelo usuário
   
    """


    query = update.callback_query
    await query.answer()
    zona = query.data.split('_')[1] # Isso estrai a zona do callback_data


    clinicas = database.get_clinics_by_zone(zona)


    if not clinicas:
         await query.edit_message_text(
              text="Desculpe, não encontrei clínicas para essa zona"
           )
         return CHOOSING_CLINIC
  
    teclado = []
    for clinica_id, nome in clinicas:
         teclado.append([InlineKeyboardButton(text=nome,
                                              callback_data=f'clinica_{clinica_id}')])
    reply_markup = InlineKeyboardMarkup(teclado)
    await query.edit_message_text(
         text = "Aqui estão as clínicas disponíveis na sua zona.\n\nEscolha 1 clinica para ver os horário",
         reply_markup=reply_markup)
        
    return CHOOSING_APPOINTMENT


   




#Passo 6: Mostrando os horários das clinica escolhida
async def show_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra os horários disponíveis para a clínica selecionada."""
    query = update.callback_query
    await query.answer()
    id_clinica = int(query.data.split('_')[1])
    agendamentos = database.get_avaliable_appointments(id_clinica)

    if not agendamentos:
        await query.edit_message_text(text="Desculpe, não há horários disponíveis. Por favor, escolha outra clínica ou digite /start.")
        return ConversationHandler.END

    teclado = []
    for agendamento_id, data_hora_str in agendamentos:
        # Converte a string da data para objeto datetime e depois formata
        data_hora_obj = datetime.fromisoformat(data_hora_str)
        texto_botao = data_hora_obj.strftime("%d/%m/%Y às %H:%M")
        teclado.append([InlineKeyboardButton(texto_botao, callback_data=f'ag_{agendamento_id}_{id_clinica}')])

    reply_markup = InlineKeyboardMarkup(teclado)
    await query.edit_message_text(text="Selecione um dos horários disponíveis:", reply_markup=reply_markup)
    # Retorna o estado correto para aguardar a escolha do horário
    return CHOOSING_APPOINTMENT



# Passo 7: Reservando o horário escolhido


async def book_selected_appointment(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE
                                   ) -> int:
       """
       Efetua a reserva do horário selecionado pelo usuário.
       """


       query= update.callback_query
       await query.answer()


       _, id_agendamento, id_clinica = query.data.split('_')
       id_agendamento = int(id_agendamento)
       user_id_telegram = query.from_user.id
       id_usuario_db = database.get_user_id(user_id_telegram)


       if not id_usuario_db:
           await query.edit_message_text("Ocorreu um erro ao identificar seu usuário. Por favor, digite /start e tente novamente.")
           return ConversationHandler.END


       sucesso = database.book_appointment(id_agendamento, id_usuario_db)


       if sucesso:
           await query.edit_message_text("✅ Agendamento confirmado com sucesso! Por favor, chegue com 15 minutos de antecedência.")
       else:
           await query.edit_message_text("❌ Desculpe, este horário não está mais disponível. Por favor, tente outro.")


       await context.bot.send_message(chat_id=query.message.chat_id, text="Se precisar de mais alguma coisa, digite /start. 😊")
       return ConversationHandler.END
   

async def book_appointment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Efetua a reserva do horário selecionado pelo usuário."""
    query = update.callback_query
    await query.answer()

    _, id_agendamento, id_clinica = query.data.split('_')
    id_agendamento = int(id_agendamento)
    user_id_telegram = query.from_user.id
    id_usuario_db = database.get_user_id(user_id_telegram)

    if not id_usuario_db:
        await query.edit_message_text("Ocorreu um erro ao identificar seu usuário. Por favor, digite /start e tente novamente.")
        return ConversationHandler.END

    sucesso = database.book_appointment(id_agendamento, id_usuario_db)

    if sucesso:
        await query.edit_message_text("✅ Agendamento confirmado com sucesso! Por favor, chegue com 15 minutos de antecedência.")
    else:
        await query.edit_message_text("❌ Desculpe, este horário não está mais disponível. Por favor, tente outro.")

    await context.bot.send_message(chat_id=query.message.chat_id, text="Se precisar de mais alguma coisa, digite /start. 😊")
    return ConversationHandler.END



# Funções auxiliares


async def como_funciona(update: Update,
                       context: ContextTypes.DEFAULT_TYPE
                       ) -> int:
   """Explica o funcionamento do bot."""
   query = update.callback_query
   await query.answer()
   mensagem = (
       "É simples! Siga os passos:\n\n"
       "1️⃣ **Clique em 'Iniciar Consulta Básica'** para começar.\n\n"
       "2️⃣ **Descreva seus sintomas** em uma única mensagem.\n\n"
       "3️⃣ **Receba orientações básicas** e, se necessário, a opção de agendar uma consulta.\n\n"
       "⚠️ **Lembre-se:** Este bot não substitui uma consulta médica profissional. Em casos de emergência, procure ajuda médica imediatamente.\n\n"
   )
   teclado = [[InlineKeyboardButton("🩺 Iniciar Consulta Básica", callback_data='iniciar_consulta')]]
   reply_markup = InlineKeyboardMarkup(teclado)
   await query.edit_message_text(text=mensagem, reply_markup=reply_markup, parse_mode="Markdown")
   return CHOOSING






async def cancelar(
                  update: Update,
                  context: ContextTypes.DEFAULT_TYPE
                  ) -> int:
   """Cancela e sai da conversa."""
   await update.message.reply_text('Operação cancelada. Se precisar de algo, digite /start.')
   return ConversationHandler.END

async def text_instead_of_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
   """Informa o usuário para usar os botões."""
   await update.message.reply_text("Por favor, utilize os botões para navegar. Digite /start para ver as opções novamente.")
   return CHOOSING
