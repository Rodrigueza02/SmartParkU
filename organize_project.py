
import shutil
import os

root = r"c:\Users\jiliana rodriguez\SmartParkU\SmartParkU"
frontend_dir = os.path.join(root, "frontend")
backend_dir = os.path.join(root, "backend")

# Ensure directories exist
os.makedirs(frontend_dir, exist_ok=True)
os.makedirs(os.path.join(backend_dir, "data"), exist_ok=True)

# Move frontend files
frontend_items = [
    "src",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "tailwind.config.ts",
    "postcss.config.mjs",
    "index.html",
    "mapa_ucc.html",
    ".next",
    "node_modules",
    ".env.local",
    "move_files.py"
]

for item in frontend_items:
    src_path = os.path.join(root, item)
    dst_path = os.path.join(frontend_dir, item)
    
    if os.path.exists(src_path):
        print(f"Moviendo {item} a frontend/")
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.move(src_path, dst_path)
        else:
            if os.path.exists(dst_path):
                os.remove(dst_path)
            shutil.move(src_path, dst_path)
    else:
        print(f"  {item} no existe en la raíz")

print("\n✅ ¡Organización completada!")
