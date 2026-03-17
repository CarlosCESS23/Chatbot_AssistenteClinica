# 🤖🩺 Bot de Pré-Triagem Médica — Telegram

Um assistente virtual de saúde para o Telegram que realiza **pré-triagem de sintomas** com inteligência artificial, orientando usuários sobre cuidados iniciais e quando buscar atendimento médico.

> ⚠️ **Aviso:** Este bot não substitui uma consulta médica profissional. Em casos de emergência, procure um pronto-socorro ou ligue para o SAMU **(192)**.

---

## 📋 Funcionalidades

- **Pré-triagem por sintomas** — O usuário descreve seus sintomas em linguagem natural e recebe orientações seguras geradas por IA.
- **Classificação de risco** — A IA classifica os sintomas em *Baixo Risco*, *Risco Moderado* ou *Alto Risco/Emergência*.
- **Análise de linguagem natural (NLP)** — Extrai automaticamente sintomas do texto do usuário usando NLTK.
- **Banco de dados de clínicas** — Armazena clínicas fictícias e agendamentos disponíveis em Manaus por zona (Norte, Sul, Leste, Oeste).
- **Interface conversacional** — Fluxo guiado por botões inline no Telegram via `ConversationHandler`.

---

## 🧰 Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| **Python 3** | Linguagem principal |
| **python-telegram-bot 20.0** | Framework para integração com a API do Telegram |
| **Google Gemini 1.5 Flash** | Modelo de IA generativa para análise de sintomas e geração de orientações |
| **google-generativeai 0.7.1** | SDK Python para acesso à API do Gemini |
| **NLTK 3.9.1** | Processamento de linguagem natural para extração de sintomas |
| **SQLite** | Banco de dados local para usuários, clínicas e agendamentos |
| **python-dotenv 1.0.1** | Gerenciamento de variáveis de ambiente via arquivo `.env` |

---

## 📁 Estrutura do Projeto

```
.
├── main.py                  # Ponto de entrada da aplicação
├── requeriment.txt          # Dependências do projeto
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore
└── chatbot/
    ├── __init__.py          # Exporta a função run()
    ├── bot.py               # Configuração e inicialização do bot
    ├── config.py            # Chaves de API, logger e inicialização do modelo Gemini
    ├── handlers.py          # Funções de callback para cada etapa da conversa
    ├── nlp.py               # Extração de sintomas com NLTK
    └── database.py          # Configuração do banco de dados SQLite e dados fictícios
```

---

## 🔁 Fluxo da Conversa

```
/start
  └─> Menu com botões inline
        ├─> [❓ Como funciona?]  →  Exibe explicação e volta ao menu
        └─> [🩺 Iniciar Consulta]  →  Solicita descrição dos sintomas
                                          └─> Usuário descreve sintomas
                                                └─> NLP extrai sintomas-chave
                                                      └─> Gemini gera orientação de saúde
```

---

## ⚙️ Como Executar

### 1. Pré-requisitos

- Python 3.10+
- Conta no [Google AI Studio](https://aistudio.google.com/) para obter a chave do Gemini
- Bot criado no Telegram via [@BotFather](https://t.me/BotFather)

### 2. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 3. Crie e ative um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 4. Instale as dependências

```bash
pip install -r requeriment.txt
```

### 5. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:

```env
API_KEY_GEMINI=sua_chave_gemini_aqui
API_KEY_CHATBOT=seu_token_telegram_aqui
```

### 6. Execute o bot

```bash
python main.py
```

---

## 🗄️ Banco de Dados

O banco de dados `clinica.db` (SQLite) é criado automaticamente na primeira execução. Ele contém três tabelas:

- **Usuarios** — Armazena o `telegram_id`, nome, histórico de sintomas e última interação.
- **Clinicas** — Clínicas públicas fictícias de Manaus com nome, endereço e zona.
- **Agendamentos** — Horários disponíveis vinculados a clínicas e usuários.

---

## 🧠 Sistema de Prompt (IA)

O modelo Gemini é configurado com um **system prompt** que impõe regras estritas de segurança médica:

- ❌ **Nunca diagnostica** doenças pelo nome.
- ❌ **Nunca prescreve** medicamentos.
- ✅ **Classifica o risco** em três níveis.
- ✅ **Fornece orientações** adequadas ao nível de risco.
- ✅ **Inclui aviso legal** ao final de cada resposta.

---

## 📦 Dependências (`requeriment.txt`)

```
python-telegram-bot==20.0
google-cloud-vision==3.7.2
google-generativeai==0.7.1
nltk==3.9.1
python-dotenv==1.0.1
```

---

## 📄 Licença

Este projeto é de uso educacional e experimental. Não deve ser utilizado como substituto de serviços médicos reais.
