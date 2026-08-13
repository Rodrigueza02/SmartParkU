
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db import SessionLocal, engine
from app.db.base import Base
from app.models import Usuario, EspacioParqueo
from app.core import get_password_hash
from app.mqtt_client import SLOTS_DEFINICION


def seed_users():
    db = SessionLocal()
    try:
        usuarios_prueba = [
            {
                "nombre": "Admin SmartParkU",
                "correo": "admin@ucc.edu.co",
                "password": "admin123",
                "rol": "SuperAdmin",
                "estado": "Activo"
            },
            {
                "nombre": "Estudiante Prueba",
                "correo": "estudiante@ucc.edu.co",
                "password": "estudiante123",
                "rol": "Estudiante",
                "estado": "Activo"
            },
            {
                "nombre": "Admin Campus",
                "correo": "admin.campus@ucc.edu.co",
                "password": "admincampus123",
                "rol": "Administrativo",
                "estado": "Activo"
            },
            {
                "nombre": "Visitante Externo",
                "correo": "visitante@gmail.com",
                "password": "visitante123",
                "rol": "Visitante",
                "estado": "Activo"
            },
            {
                "nombre": "Usuario Inactivo",
                "correo": "inactivo@ucc.edu.co",
                "password": "password123",
                "rol": "Estudiante",
                "estado": "Inactivo"
            }
        ]

        print("\n── Usuarios ──────────────────────────────────────────")
        for u_data in usuarios_prueba:
            exists = db.query(Usuario).filter(Usuario.correo == u_data["correo"]).first()
            if not exists:
                new_user = Usuario(
                    nombre=u_data["nombre"],
                    correo=u_data["correo"],
                    password=get_password_hash(u_data["password"]),
                    rol=u_data["rol"],
                    estado=u_data["estado"]
                )
                db.add(new_user)
                print(f"  ✅ Creado: {u_data['correo']} ({u_data['rol']})")
            else:
                print(f"  ℹ️  Ya existe: {u_data['correo']}")

        db.commit()
        print("Usuarios OK.\n")

    except Exception as e:
        print(f"  ❌ Error en seed de usuarios: {e}")
        db.rollback()
    finally:
        db.close()


def seed_espacios():
    db = SessionLocal()
    try:
        print("── Espacios de parqueo ───────────────────────────────")
        creados = 0
        for s in SLOTS_DEFINICION:
            existe = db.query(EspacioParqueo).filter_by(slot_id=s["slot_id"]).first()
            if not existe:
                espacio = EspacioParqueo(
                    slot_id=s["slot_id"],
                    label=s["label"],
                    tipo=s["tipo"],
                    status="libre",
                )
                db.add(espacio)
                print(f"  ✅ Creado: {s['slot_id']} ({s['label']}) - {s['tipo']}")
                creados += 1
            else:
                print(f"  ℹ️  Ya existe: {s['slot_id']} ({s['label']})")

        db.commit()
        print(f"Espacios OK - {creados} nuevos, {len(SLOTS_DEFINICION) - creados} ya existían.\n")

    except Exception as e:
        print(f"  ❌ Error en seed de espacios: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("═══════════════════════════════════════════════════════")
    print("  SmartParkU - Seeding inicial de base de datos")
    print("═══════════════════════════════════════════════════════")
    seed_users()
    seed_espacios()
    print("═══════════════════════════════════════════════════════")
    print("  ¡Seeding completado! Ya puedes iniciar el backend.")
    print("═══════════════════════════════════════════════════════")

