# back/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Copia o arquivo de dependências da raiz do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia apenas o código do backend para o contêiner
COPY ./back .

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]