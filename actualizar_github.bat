@echo off
echo 🚀 ACTUALIZANDO PROYECTO EN GITHUB
echo =====================================

cd /d C:\Users\aluni\absentismoespana

echo.
echo 📋 Estado actual de Git:
git status

echo.
echo 🗑️ Eliminando carpetas no necesarias...
rmdir /S /Q scripts\json_extractors 2>nul
rmdir /S /Q scripts\csv_extractors 2>nul
rmdir /S /Q scripts\shared 2>nul
rmdir /S /Q scripts\data 2>nul

echo.
echo 📝 Agregando todos los cambios...
git add -A

echo.
echo 💾 Creando commit...
git commit -m "Refactorización: Mantener solo funcionalidad de descarga CSV" -m "- Eliminados scripts de análisis y procesamiento" -m "- Simplificada estructura del proyecto" -m "- Actualizado requirements.txt con dependencias mínimas" -m "- Renombrado csv_extractors a extractors" -m "- Actualizada documentación README.md" -m "- Eliminados archivos obsoletos y temporales"

echo.
echo 📤 Subiendo cambios a GitHub...
git push origin main

echo.
echo ✅ ACTUALIZACIÓN COMPLETADA
echo.
echo 🏷️ (Opcional) Crear tag de versión:
echo    git tag -a v2.0.0 -m "Versión 2.0: Solo descarga de CSVs"
echo    git push origin v2.0.0
echo.
pause
