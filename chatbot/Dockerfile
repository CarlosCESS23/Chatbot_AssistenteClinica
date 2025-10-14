# chatbot/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt stopwords

# Copia o código do chatbot e o script principal
COPY chatbot ./chatbot
COPY main.py .

# Comando para iniciar o bot
CMD ["python", "main.py"]