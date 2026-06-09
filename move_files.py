
import shutil
import os

root_dir = r"c:\Users\jiliana rodriguez\SmartParkU\SmartParkU"
frontend_dir = os.path.join(root_dir, "frontend")

# Create frontend directory if not exists
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)

# List of frontend files/directories to move
files_to_move = [
    "src",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "tailwind.config.ts",
    "postcss.config.mjs",
    "index.html",
    "mapa_ucc.html"
]

for item in files_to_move:
    src = os.path.join(root_dir, item)
    dst = os.path.join(frontend_dir, item)
    
    if os.path.exists(src):
        print(f"Moviendo {item} a frontend/")
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.move(src, dst)
        else:
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(src, dst)
    else:
        print(f"{item} no encontrado en el root")

print("Movimiento de archivos de frontend completado!")
