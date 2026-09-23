#!/bin/bash
# Script de inicio del backend que espera la BD, aplica migraciones e inicia el servidor

set -e  # Salir si cualquier comando falla

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SmartParkU - Iniciando en producción"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "🔄 Esperando a que la base de datos esté lista..."
python << END
import time
import psycopg

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        # Conectar directamente con los parámetros
        conn = psycopg.connect(
            host="db",
            port=5432,
            dbname="smartparku",
            user="postgres",
            password="postgres"
        )
        conn.close()
        print("✅ Base de datos conectada!")
        break
    except Exception as e:
        attempt += 1
        if attempt == max_attempts:
            print(f"❌ Error: No se pudo conectar a la base de datos después de {max_attempts} intentos")
            print(f"Error: {e}")
            exit(1)
        print(f"⏳ Intento {attempt}/{max_attempts}... Reintentando en 2 segundos")
        time.sleep(2)
END

echo "🔄 Aplicando migraciones de Alembic..."
alembic upgrade head

echo "✅ Migraciones aplicadas correctamente"

echo "🔄 Poblando datos iniciales..."
python -m app.initial_data

echo "🚀 Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
