#!/bin/bash
# Script para commit inicial - AbsentismoEspana
# Fecha: 6 Junio 2025

echo "=== PREPARANDO COMMIT INICIAL PARA GITHUB ==="
echo ""

# Verificar estado actual
echo "1. Estado actual de Git:"
git status

echo ""
echo "2. Archivos que se van a añadir:"
echo "   - .gitignore (protección de credenciales)"
echo "   - scripts/ (código principal)"
echo "   - config/database.env.template (plantilla segura)"
echo "   - urls_etcl_completo.json (configuración final)"
echo "   - Archivos del 30 Mayo o posteriores"

echo ""
echo "3. Archivos EXCLUIDOS (por .gitignore):"
echo "   - config/database.env (credenciales reales)"
echo "   - venv/ (entorno virtual)"
echo "   - __pycache__/ (cache Python)"
echo "   - data/raw/ y data/processed/ (archivos grandes)"

echo ""
read -p "¿Continuar con el commit inicial? (s/n): " respuesta

if [[ $respuesta == "s" || $respuesta == "S" ]]; then
    echo ""
    echo "=== EJECUTANDO COMMIT INICIAL ==="
    
    # Añadir archivos al staging
    git add .gitignore
    git add config/database.env.template
    git add scripts/
    git add urls_etcl_completo.json
    git add *.py
    git add *.json
    git add *.docx
    git add informes/
    git add logs/
    
    # Verificar qué se va a commitear
    echo ""
    echo "Archivos en staging:"
    git status --porcelain
    
    echo ""
    read -p "¿Hacer commit? (s/n): " commit_respuesta
    
    if [[ $commit_respuesta == "s" || $commit_respuesta == "S" ]]; then
        # Commit inicial
        git commit -m "Initial commit: AbsentismoEspana project

- Sistema de extracción de datos de absentismo del INE
- Scripts para descarga y procesamiento de CSVs
- Configuración de URLs para ETCL (Encuesta Trimestral Coste Laboral)
- Estructura de base de datos PostgreSQL
- Protección de credenciales con .gitignore

Fecha: 30 Mayo 2025 (archivos finales)
Enfoque: Extracción directa de CSVs desde APIs del INE"
        
        echo ""
        echo "✅ COMMIT INICIAL COMPLETADO"
        echo ""
        echo "Próximo paso: Crear repositorio en GitHub"
        echo "Comando para conectar: git remote add origin <URL_GITHUB>"
    else
        echo "Commit cancelado"
    fi
else
    echo "Operación cancelada"
fi

echo ""
echo "=== SCRIPT COMPLETADO ==="
