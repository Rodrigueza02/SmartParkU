#!/bin/bash
# Script de inicio del backend que aplica migraciones y luego inicia el servidor

set -e  # Salir si cualquier comando falla

echo "🔄 Esperando a que la base de datos esté lista..."
python << END
import time
import psycopg
from app.core.config import settings

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        conn = psycopg.connect(settings.DATABASE_URL)
        conn.close()
        print("✅ Base de datos conectada!")
        break
    except Exception as e:
        attempt += 1
        if attempt == max_attempts:
            print(f"❌ Error: No se pudo conectar a la base de datos después de {max_attempts} intentos")
            exit(1)
        print(f"⏳ Intento {attempt}/{max_attempts}... Reintentando en 2 segundos")
        time.sleep(2)
END

echo "🔄 Aplicando migraciones de Alembic..."
alembic upgrade head

echo "✅ Migraciones aplicadas correctamente"

echo "🚀 Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
