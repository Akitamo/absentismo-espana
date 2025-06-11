@echo off
REM descarga_masiva.bat - Script para ejecutar la descarga completa de CSVs del INE
REM Ubicación: scripts\descarga\descarga_masiva.bat

echo ============================================
echo  DESCARGA MASIVA DE CSVs DEL INE
echo ============================================
echo.

REM Ir al directorio del script
cd /d "%~dp0"

echo Directorio actual: %CD%
echo.

echo Iniciando descarga completa...
echo ============================================
echo.

REM Ejecutar el script de descarga
python ejecutar_descarga_completa.py

echo.
echo ============================================
echo Proceso completado.
echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
