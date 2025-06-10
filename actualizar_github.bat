@echo off
REM actualizar_github_v2.bat - Script para actualizar proyecto en GitHub
REM Cambiar a la carpeta donde está este script
cd /d "%~dp0"

echo ================================================
echo   ACTUALIZANDO PROYECTO EN GITHUB - v2.0
echo ================================================
echo.
echo 📁 Directorio del proyecto: %CD%
echo.

REM Verificar que estamos en un repositorio git
git status >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: No se encontró repositorio Git
    echo    Asegúrate de estar en el directorio correcto
    pause
    exit /b 1
)

echo 📋 Estado actual de Git:
git status --short
echo.

echo 🗑️ Eliminando carpetas no necesarias...
if exist "scripts\json_extractors" (
    rmdir /S /Q scripts\json_extractors 2>nul
    echo    ✅ Eliminada: scripts\json_extractors
)
if exist "scripts\csv_extractors" (
    rmdir /S /Q scripts\csv_extractors 2>nul
    echo    ✅ Eliminada: scripts\csv_extractors
)
if exist "scripts\shared" (
    rmdir /S /Q scripts\shared 2>nul
    echo    ✅ Eliminada: scripts\shared
)
if exist "scripts\data" (
    rmdir /S /Q scripts\data 2>nul
    echo    ✅ Eliminada: scripts\data
)
echo.

echo 📝 Agregando todos los cambios...
git add -A
echo.

echo 💾 Creando commit...
git commit -m "v2.0: Proyecto portable y simplificado" -m "CAMBIOS PRINCIPALES:" -m "- Proyecto ahora es portable entre diferentes equipos/usuarios" -m "- Eliminados todos los scripts de análisis" -m "- Mantenida solo funcionalidad de descarga CSV" -m "- Actualizado README con instrucciones completas" -m "- Agregado script setup_proyecto.bat para configuración inicial" -m "- Todas las rutas ahora son relativas" -m "- Estructura simplificada y documentada"

if errorlevel 1 (
    echo.
    echo ⚠️  No hay cambios para hacer commit o hubo un error
    echo.
) else (
    echo ✅ Commit creado exitosamente
    echo.
)

echo 📤 Subiendo cambios a GitHub...
git push origin main

if errorlevel 1 (
    echo.
    echo ❌ Error al subir cambios. Posibles causas:
    echo    - No tienes permisos de escritura
    echo    - La rama remota tiene cambios que no tienes localmente
    echo    - Problemas de conexión
    echo.
    echo Intenta: git pull origin main
    echo Y luego ejecuta este script nuevamente
) else (
    echo.
    echo ✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE
    echo.
    echo 🏷️ (Opcional) Crear tag de versión:
    echo    git tag -a v2.0.0 -m "Versión 2.0: Proyecto portable, solo descarga CSVs"
    echo    git push origin v2.0.0
)

echo.
pause
