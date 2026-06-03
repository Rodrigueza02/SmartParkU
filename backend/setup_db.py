import psycopg
from psycopg import sql
import os
from dotenv import load_dotenv

load_dotenv()


def ensure_db_exists():
    """Crea la base de datos 'smartparku' si no existe."""
    db_url = os.getenv("DATABASE_URL")
    # Formato en .env: postgresql+psycopg://user:pass@host:port/dbname
    # psycopg.connect necesita: postgresql://user:pass@host:port/dbname
    # Eliminamos el driver hint (+psycopg) para la conexión directa con psycopg
    clean_url  = db_url.replace("postgresql+psycopg://", "postgresql://")
    base_url   = clean_url.rsplit('/', 1)[0] + '/postgres'
    target_db  = clean_url.rsplit('/', 1)[1]

    try:
        conn = psycopg.connect(base_url, autocommit=True)
        cur  = conn.cursor()

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


def seed_espacios():
    """
    Pobla la tabla 'espacios_parqueo' con los 10 espacios fijos del parqueadero UCC Pasto.
    Si un espacio ya existe (por slot_id) no lo duplica (upsert).
    """
    from database import engine, SessionLocal
    import models

    # Crear tablas si no existen
    models.Base.metadata.create_all(bind=engine)

    # Definición canónica de los 10 espacios — sincronizada con mqtt_client.SLOTS_DEFINICION
    slots = [
        {"slot_id": "slot_01", "label": "C-01", "tipo": "carro"},
        {"slot_id": "slot_02", "label": "C-02", "tipo": "carro"},
        {"slot_id": "slot_03", "label": "C-03", "tipo": "carro"},
        {"slot_id": "slot_04", "label": "C-04", "tipo": "carro"},
        {"slot_id": "slot_05", "label": "M-01", "tipo": "moto"},
        {"slot_id": "slot_06", "label": "M-02", "tipo": "moto"},
        {"slot_id": "slot_07", "label": "M-03", "tipo": "moto"},
        {"slot_id": "slot_08", "label": "B-01", "tipo": "bicicleta"},
        {"slot_id": "slot_09", "label": "B-02", "tipo": "bicicleta"},
        {"slot_id": "slot_10", "label": "V-01", "tipo": "vip"},
    ]

    db = SessionLocal()
    try:
        creados = 0
        for s in slots:
            existente = db.query(models.EspacioParqueo).filter_by(slot_id=s["slot_id"]).first()
            if not existente:
                espacio = models.EspacioParqueo(
                    slot_id=s["slot_id"],
                    label=s["label"],
                    tipo=s["tipo"],
                    status="libre",
                )
                db.add(espacio)
                creados += 1
        db.commit()
        print(f"Espacios de parqueo: {creados} creados, {len(slots) - creados} ya existían.")
    except Exception as e:
        db.rollback()
        print(f"Error al poblar espacios: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    ensure_db_exists()
    seed_espacios()
