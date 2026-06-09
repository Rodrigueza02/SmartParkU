
import os
import shutil

root = os.path.join(os.path.dirname(__file__))
frontend = os.path.join(root, "frontend")
backend_data = os.path.join(root, "backend", "data")

# Create directories
os.makedirs(frontend, exist_ok=True)
os.makedirs(backend_data, exist_ok=True)
print(f"✅ Created directories:")
print(f"   - {frontend}")
print(f"   - {backend_data}")

# Now move items
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
    "organize_project.py"
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
        print(f"✅ Moved {item}")

print("\n🎉 All done!")
