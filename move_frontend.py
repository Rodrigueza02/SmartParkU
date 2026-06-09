
import os
import shutil

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    
    # Step 1: Create frontend directory
    print(f"1. Creando carpeta frontend en: {frontend_dir}")
    if not os.path.exists(frontend_dir):
        os.makedirs(frontend_dir, exist_ok=True)
        print("   ✅ Carpeta creada!")
    else:
        print("   ℹ️  Carpeta ya existe")
    
    # Step 2: List of files and folders to move
    items_to_move = [
        ".next",
        "node_modules",
        "src",
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        "tailwind.config.ts",
        "postcss.config.mjs",
        "index.html",
        "mapa_ucc.html",
        ".env.local",
        "move_files.py",
        "organize_project.py",
        "create_folders.py"
    ]
    
    # Step 3: Move each item
    print("\n2. Moviendo archivos a frontend/:")
    for item in items_to_move:
        src = os.path.join(root_dir, item)
        dst = os.path.join(frontend_dir, item)
        
        if not os.path.exists(src):
            print(f"   ⚠️  {item}: No encontrado en raíz")
            continue
            
        print(f"   📦 {item} -> frontend/")
        
        # Clean destination if exists
        if os.path.exists(dst):
            try:
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            except Exception as e:
                print(f"   ❌ No se pudo limpiar destino: {e}")
                continue
        
        # Move the item
        try:
            shutil.move(src, dst)
            print(f"      ✅ Listo!")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print("\n3. ¡Proceso completado! 🎉")
    print(f"   Frontend organizado en: {frontend_dir}")

if __name__ == "__main__":
    main()
