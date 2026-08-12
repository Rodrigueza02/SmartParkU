# Etapa 1: Build de Next.js
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar dependencias primero para aprovechar caché de Docker
COPY package*.json ./
RUN npm install --frozen-lockfile

# Copiar el resto del proyecto y compilar
COPY . .
RUN npm run build

# ─────────────────────────────────────────────────────────────────────────────
# Etapa 2: Imagen de producción (más liviana)
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copiar solo lo necesario desde la etapa de build
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# Exponer el puerto de Next.js
EXPOSE 3000

# Comando de inicio en producción
CMD ["npm", "start"]
