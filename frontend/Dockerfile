# Etapa única: build y serve con Next.js
FROM node:20-alpine

WORKDIR /app

# Build arguments
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL

# Set as environment variables for build
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL

# Instalar dependencias
COPY package*.json ./
RUN npm install --legacy-peer-deps --frozen-lockfile

# Copiar el proyecto y compilar
COPY . .
RUN npm run build

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

CMD ["npm", "start"]
