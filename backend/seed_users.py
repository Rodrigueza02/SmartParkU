from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth


def seed_users():
    """Pobla la tabla 'usuarios' con cuentas de prueba para cada rol de la UCC."""
    models.Base.metadata.create_all(bind=engine)

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
            exists = db.query(models.Usuario).filter(
                models.Usuario.correo == u_data["correo"]
            ).first()
            if not exists:
                new_user = models.Usuario(
                    nombre=u_data["nombre"],
                    correo=u_data["correo"],
                    password=auth.get_password_hash(u_data["password"]),
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
    """
    Pobla la tabla 'espacios_parqueo' con los 10 espacios fijos del parqueadero UCC Pasto.
    No duplica si el slot_id ya existe (upsert seguro).
    """
    models.Base.metadata.create_all(bind=engine)

    # Definición canónica sincronizada con mqtt_client.SLOTS_DEFINICION
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
        print("── Espacios de parqueo ───────────────────────────────")
        creados = 0
        for s in slots:
            existe = db.query(models.EspacioParqueo).filter_by(slot_id=s["slot_id"]).first()
            if not existe:
                espacio = models.EspacioParqueo(
                    slot_id=s["slot_id"],
                    label=s["label"],
                    tipo=s["tipo"],
                    status="libre",
                )
                db.add(espacio)
                print(f"  ✅ Creado: {s['slot_id']} ({s['label']}) — {s['tipo']}")
                creados += 1
            else:
                print(f"  ℹ️  Ya existe: {s['slot_id']} ({s['label']})")

        db.commit()
        print(f"Espacios OK — {creados} nuevos, {len(slots) - creados} ya existían.\n")

    except Exception as e:
        print(f"  ❌ Error en seed de espacios: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("═══════════════════════════════════════════════════════")
    print("  SmartParkU — Seeding inicial de base de datos")
    print("═══════════════════════════════════════════════════════")
    seed_users()
    seed_espacios()
    print("═══════════════════════════════════════════════════════")
    print("  ¡Seeding completado! Ya puedes iniciar el backend.")
    print("═══════════════════════════════════════════════════════")
