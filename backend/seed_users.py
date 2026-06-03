from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth

def seed_data():
    # Crear tablas si no existen
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Lista de usuarios de prueba para la UCC
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

        print("Insertando usuarios de prueba en SmartParkU...")

        for u_data in usuarios_prueba:
            # Verificar si el usuario ya existe
            exists = db.query(models.Usuario).filter(models.Usuario.correo == u_data["correo"]).first()
            if not exists:
                new_user = models.Usuario(
                    nombre=u_data["nombre"],
                    correo=u_data["correo"],
                    password=auth.get_password_hash(u_data["password"]), # Encriptación Bcrypt
                    rol=u_data["rol"],
                    estado=u_data["estado"]
                )
                db.add(new_user)
                print(f"✅ Usuario creado: {u_data['correo']} ({u_data['rol']})")
            else:
                print(f"ℹ️ El usuario {u_data['correo']} ya existe. Saltando...")

        db.commit()
        print("\n¡Seeding completado exitosamente! Ya puedes probar el Login.")

    except Exception as e:
        print(f"❌ Error durante el seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
