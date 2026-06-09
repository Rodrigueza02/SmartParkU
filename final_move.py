
import os
import shutil

root = r"c:\Users\jiliana rodriguez\SmartParkU\SmartParkU"
frontend = os.path.join(root, "frontend")
backend_data = os.path.join(root, "backend", "data")

# Create backend/data folder
os.makedirs(backend_data, exist_ok=True)

# List of items to move
items = [
    "src",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "tailwind.config.ts",
    "postcss.config.mjs",
    "index.html",
    "mapa_ucc.html",
    ".env.local",
    "create_folders.py",
    "move_files.py",
    "move_frontend.py",
    "organize_project.py",
    "just_create_folder.py"
]

for item in items:
    src = os.path.join(root, item)
    dst = os.path.join(frontend, item)
    if os.path.exists(src):
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, dst)
        print(f"Moved {item}")
    else:
        print(f"Skipped {item}")

print("\n✅ All items moved to frontend/!")
