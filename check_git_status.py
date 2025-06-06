import subprocess
import os

# Ir al directorio del proyecto
os.chdir(r"C:\Users\slunagda\AbsentismoEspana")

# Verificar estado de git
print("=== ESTADO ACTUAL DE GIT ===")
try:
    result = subprocess.run(["git", "status"], capture_output=True, text=True, shell=True)
    print(result.stdout)
    if result.stderr:
        print("Errores:", result.stderr)
except Exception as e:
    print(f"Error ejecutando git status: {e}")
