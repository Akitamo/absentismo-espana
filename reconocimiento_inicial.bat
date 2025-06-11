@echo off
REM reconocimiento_inicial.bat - Ejecuta el análisis de reconocimiento inicial
REM Ubicación: C:\Users\%USERPROFILE%\absentismoespana\

echo ============================================
echo  RECONOCIMIENTO INICIAL DE ARCHIVOS CSV
echo ============================================
echo.

cd /d "%~dp0"
cd scripts\analysis\exploratory

echo Ejecutando reconocimiento inicial...
echo.

python reconocimiento_inicial.py

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
