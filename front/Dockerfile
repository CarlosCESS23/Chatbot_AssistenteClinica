# front/Dockerfile

# ---- Estágio de Build ----
FROM oven/bun:1 as build-stage
WORKDIR /app

# Instala as dependências (permitindo a atualização do lockfile)
COPY package.json bun.lockb ./
RUN bun install

# Copia o código fonte
COPY . .

# Compila o projeto para produção
RUN bun run build

# ---- Estágio de Serviço ----
FROM nginx:alpine as serve-stage

# Copia os arquivos compilados do estágio anterior
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copia a configuração personalizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80
EXPOSE 80

# Inicia o Nginx
CMD ["nginx", "-g", "daemon off;"]