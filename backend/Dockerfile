# Imagen base de Python 3.13 slim
FROM python:3.13-slim

# Evitar que Python guarde los logs en buffer
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para PostgreSQL y compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar dependencias de Python primero (capa cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend
COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando de inicio — en docker-compose se sobreescribe con --reload para desarrollo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
