import subprocess
import os
from pathlib import Path

# Ir al directorio del proyecto
project_dir = Path(__file__).resolve().parent
os.chdir(project_dir)

# Verificar estado de git
print("=== ESTADO ACTUAL DE GIT ===")
try:
    result = subprocess.run(["git", "status"], capture_output=True, text=True, shell=True)
    print(result.stdout)
    if result.stderr:
        print("Errores:", result.stderr)
except Exception as e:
    print(f"Error ejecutando git status: {e}")
