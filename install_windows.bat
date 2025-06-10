@echo off
echo =====================================================
echo   INSTALACION RAPIDA - AbsentismoEspana
echo =====================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python 3.8 o superior desde python.org
    pause
    exit /b 1
)

echo [1/5] Python detectado
echo.

REM Crear entorno virtual
echo [2/5] Creando entorno virtual...
if exist venv (
    echo      El entorno virtual ya existe
) else (
    python -m venv venv
    echo      Entorno virtual creado
)
echo.

REM Activar entorno virtual
echo [3/5] Activando entorno virtual...
call venv\Scripts\activate.bat
echo      Entorno activado
echo.

REM Instalar dependencias
echo [4/5] Instalando dependencias...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
echo      Dependencias instaladas
echo.

REM Ejecutar setup
echo [5/5] Configurando proyecto...
python setup_project.py
echo.

echo =====================================================
echo   INSTALACION COMPLETADA
echo =====================================================
echo.
echo Para empezar a trabajar:
echo   1. venv\Scripts\activate
echo   2. cd scripts\csv_extractors
echo   3. python ejecutar_descarga_masiva.py
echo.
pause
