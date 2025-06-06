#!/usr/bin/env python3
"""
Script para commit inicial - AbsentismoEspana
Preparación para GitHub
Fecha: 6 Junio 2025
"""

import os
import subprocess
import sys

def run_git_command(command):
    """Ejecuta un comando de git y retorna el resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("=== PREPARANDO COMMIT INICIAL PARA GITHUB ===")
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('.git'):
        print("❌ ERROR: No se encontró repositorio Git (.git)")
        print("Ejecuta este script desde la raíz del proyecto AbsentismoEspana")
        return
    
    print("✅ Repositorio Git encontrado")
    print()
    
    # Verificar estado actual
    print("1. ESTADO ACTUAL DE GIT:")
    success, output, error = run_git_command("git status --porcelain")
    if success:
        if output.strip():
            print("   Archivos modificados/nuevos detectados:")
            for line in output.strip().split('\n'):
                print(f"   {line}")
        else:
            print("   ✅ No hay cambios pendientes")
    else:
        print(f"   ❌ Error: {error}")
    
    print()
    print("2. ARCHIVOS QUE SE VAN A AÑADIR:")
    archivos_incluir = [
        "✅ .gitignore (protección de credenciales)",
        "✅ scripts/ (código principal)", 
        "✅ config/database.env.template (plantilla segura)",
        "✅ urls_etcl_completo.json (configuración final)",
        "✅ Archivos Python del 30 Mayo+",
        "✅ Documentación del proyecto"
    ]
    
    for archivo in archivos_incluir:
        print(f"   {archivo}")
    
    print()
    print("3. ARCHIVOS EXCLUIDOS (por .gitignore):")
    archivos_excluir = [
        "🔒 config/database.env (credenciales reales)",
        "🔒 venv/ (entorno virtual)",
        "🔒 __pycache__/ (cache Python)",
        "🔒 data/raw/ y data/processed/ (archivos grandes)",
        "🔒 logs/ (archivos de log)"
    ]
    
    for archivo in archivos_excluir:
        print(f"   {archivo}")
    
    print()
    respuesta = input("¿Continuar con el commit inicial? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        print()
        print("=== EJECUTANDO COMMIT INICIAL ===")
        
        # Añadir archivos específicos al staging
        archivos_git = [
            ".gitignore",
            "config/database.env.template", 
            "scripts/",
            "urls_etcl_completo.json",
            "*.py",
            "*.json", 
            "*.docx",
            "informes/",
            "logs/"
        ]
        
        print("📦 Añadiendo archivos al staging...")
        for archivo in archivos_git:
            success, output, error = run_git_command(f"git add {archivo}")
            if success:
                print(f"   ✅ {archivo}")
            else:
                print(f"   ⚠️  {archivo} (puede no existir)")
        
        # Verificar qué se va a commitear
        print()
        print("📋 ARCHIVOS EN STAGING:")
        success, output, error = run_git_command("git status --cached --porcelain")
        if success and output.strip():
            for line in output.strip().split('\n'):
                print(f"   {line}")
        else:
            print("   (No hay archivos en staging)")
        
        print()
        commit_respuesta = input("¿Hacer commit? (s/n): ").lower().strip()
        
        if commit_respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            # Mensaje de commit
            commit_message = """Initial commit: AbsentismoEspana project

- Sistema de extracción de datos de absentismo del INE
- Scripts para descarga y procesamiento de CSVs  
- Configuración de URLs para ETCL (Encuesta Trimestral Coste Laboral)
- Estructura de base de datos PostgreSQL
- Protección de credenciales con .gitignore

Fecha: 30 Mayo 2025 (archivos finales)
Enfoque: Extracción directa de CSVs desde APIs del INE"""
            
            print("💾 Ejecutando commit...")
            success, output, error = run_git_command(f'git commit -m "{commit_message}"')
            
            if success:
                print()
                print("✅ COMMIT INICIAL COMPLETADO")
                print()
                print("🎯 PRÓXIMOS PASOS:")
                print("1. Ir a GitHub.com")
                print("2. Crear nuevo repositorio 'AbsentismoEspana'")
                print("3. Copiar la URL del repositorio")
                print("4. Ejecutar: git remote add origin <URL_GITHUB>")
                print("5. Ejecutar: git push -u origin main")
            else:
                print(f"❌ Error en commit: {error}")
        else:
            print("📝 Commit cancelado")
    else:
        print("🚫 Operación cancelada")
    
    print()
    print("=== SCRIPT COMPLETADO ===")

if __name__ == "__main__":
    main()
