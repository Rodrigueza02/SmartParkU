import psycopg
from psycopg import sql
import os
from dotenv import load_dotenv

load_dotenv()

def ensure_db_exists():
    # Obtener la URL de la base de datos y extraer componentes
    db_url = os.getenv("DATABASE_URL")
    # Formato: postgresql+psycopg://user:pass@host:port/dbname
    
    # Para crear la base de datos, necesitamos conectarnos a la base de datos 'postgres' por defecto
    base_url = db_url.rsplit('/', 1)[0] + '/postgres'
    target_db = db_url.rsplit('/', 1)[1]

    try:
        # Conectarse a 'postgres' para crear la base de datos objetivo
        conn = psycopg.connect(base_url, autocommit=True)
        cur = conn.cursor()
        
        # Verificar si la base de datos existe
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creando base de datos '{target_db}'...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
            print("Base de datos creada exitosamente.")
        else:
            print(f"La base de datos '{target_db}' ya existe.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al verificar/crear la base de datos: {e}")

if __name__ == "__main__":
    ensure_db_exists()
