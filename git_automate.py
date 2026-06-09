import subprocess
import sys
import os

repo_dir = r"c:\Users\jiliana rodriguez\SmartParkU\SmartParkU"
os.chdir(repo_dir)

def run_command(cmd):
    print(f"▶️  Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"✅ Salida:")
    print(result.stdout)
    if result.stderr:
        print(f"⚠️  Error:")
        print(result.stderr)
    return result

# 1. Status
print("\n=== 1. git status")
run_command("git status")

# 2. Add changes
print("\n=== 2. git add .")
run_command("git add .")
run_command("git status")

# 3. Commit
print("\n=== 3. git commit")
commit_result = run_command('git commit -m "Reorganizar estructura del proyecto: backend con patrón de repositorio, frontend y mobile en carpetas separadas"')

# 4. Push
print("\n=== 4. git push")
if "nothing to commit" not in commit_result.stdout:
    run_command("git push origin feature/juliana-backend-10slots")
else:
    print("\n✅ No hay cambios nuevos cambios para commitear.")
