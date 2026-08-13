# Etapa 1: Build de Next.js
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install --frozen-lockfile

COPY . .
RUN npm run build

# ─────────────────────────────────────────────────────────────────────────────
# Etapa 2: Imagen de producción usando el output standalone de Next.js
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copiar el servidor standalone generado por Next.js
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
