#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
#  SmartParkU — Script de deploy/actualización en EC2
#  Ejecutar después de install.sh, o cada vez que haya cambios en el repo
# ═══════════════════════════════════════════════════════════════════════════════
set -e

APP_DIR="$HOME/SmartParkU"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SmartParkU - Deploy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Verificar que existe .env.production ──────────────────────────────────────
if [ ! -f "$APP_DIR/.env.production" ]; then
    echo ""
    echo "  ❌ ERROR: No se encontró .env.production"
    echo ""
    echo "  Crear el archivo primero:"
    echo "     cp $APP_DIR/.env.production.example $APP_DIR/.env.production"
    echo "     nano $APP_DIR/.env.production"
    echo "  (rellenar todos los valores y guardar con Ctrl+X, Y, Enter)"
    echo ""
    exit 1
fi

echo "▶ Actualizando código desde GitHub..."
cd "$APP_DIR"
git pull origin main

echo "▶ Construyendo y levantando contenedores..."
docker-compose -f docker-compose.prod.yml up --build -d

echo "▶ Esperando que el backend esté listo..."
sleep 10

echo "▶ Estado de los contenedores:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Deploy completado"
echo ""
# Obtener IP pública de la instancia
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "IP_PUBLICA")
echo "  Backend: http://$PUBLIC_IP:8000"
echo "  Swagger: http://$PUBLIC_IP:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
