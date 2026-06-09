
import os

root = r"c:\Users\jiliana rodriguez\SmartParkU\SmartParkU"

# Create data folder in backend
data_folder = os.path.join(root, "backend", "data")
os.makedirs(data_folder, exist_ok=True)

# Create frontend folder and move items
frontend_folder = os.path.join(root, "frontend")
os.makedirs(frontend_folder, exist_ok=True)

frontend_items = [
    "src",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "tailwind.config.ts",
    "postcss.config.mjs",
    "index.html",
    "mapa_ucc.html",
    "organize_project.py",
    "move_files.py"
]

for item in frontend_items:
    src = os.path.join(root, item)
    dst = os.path.join(frontend_folder, item)
    
    if os.path.exists(src):
        try:
            if os.path.exists(dst):
                import shutil
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            os.rename(src, dst)
            print(f"Moved {item} to frontend/")
        except Exception as e:
            print(f"Error moving {item}: {e}")

print("\n✅ All folders created!")
