@echo off
echo ========================================
echo ACTUALIZANDO PROYECTO EN GITHUB
echo ========================================
echo.

REM Verificar estado
echo Estado actual del repositorio:
git status
echo.

REM Preguntar si continuar
set /p continuar="Deseas continuar con el commit? (S/N): "
if /i "%continuar%" neq "S" (
    echo Operacion cancelada.
    pause
    exit /b
)

REM Pedir mensaje de commit
echo.
set /p mensaje="Introduce el mensaje del commit: "

REM Agregar todos los cambios
echo.
echo Agregando cambios...
git add .

REM Commit con el mensaje proporcionado
echo.
echo Creando commit...
git commit -m "%mensaje%"

REM Push a GitHub
echo.
echo Subiendo a GitHub...
git push origin main

echo.
echo ========================================
echo ACTUALIZACION COMPLETADA
echo ========================================
echo.
pause
