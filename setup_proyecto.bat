@echo off
REM setup_proyecto.bat - Script de configuración inicial del proyecto

echo ===============================================
echo   CONFIGURACIÓN INICIAL - ABSENTISMO ESPAÑA
echo ===============================================
echo.

REM Obtener el directorio del proyecto
set PROYECTO_DIR=%~dp0
echo 📁 Directorio del proyecto: %PROYECTO_DIR%
echo.

REM Verificar que estamos en el directorio correcto
if not exist "%PROYECTO_DIR%convert_docx_to_json_enhanced.py" (
    echo ❌ ERROR: No se encontró el archivo principal del proyecto
    echo    Asegúrate de ejecutar este script desde la raíz del proyecto
    pause
    exit /b 1
)

echo ✅ Directorio del proyecto verificado
echo.

echo 🔧 INSTALANDO DEPENDENCIAS...
echo =====================================

REM Verificar si existe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo    Por favor, instala Python 3.8 o superior
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version
echo.

REM Crear entorno virtual si no existe
if not exist "%PROYECTO_DIR%venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)
echo.

REM Activar entorno virtual
echo 🔄 Activando entorno virtual...
call "%PROYECTO_DIR%venv\Scripts\activate.bat"
echo ✅ Entorno virtual activado
echo.

REM Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias del proyecto...
pip install -r requirements.txt
echo ✅ Dependencias instaladas
echo.

echo 📁 CREANDO ESTRUCTURA DE DIRECTORIOS...
echo =====================================

REM Crear directorios necesarios
if not exist "%PROYECTO_DIR%logs" mkdir "%PROYECTO_DIR%logs"
if not exist "%PROYECTO_DIR%data" mkdir "%PROYECTO_DIR%data"
if not exist "%PROYECTO_DIR%data\raw" mkdir "%PROYECTO_DIR%data\raw"
if not exist "%PROYECTO_DIR%data\raw\csv" mkdir "%PROYECTO_DIR%data\raw\csv"
if not exist "%PROYECTO_DIR%data\processed" mkdir "%PROYECTO_DIR%data\processed"
if not exist "%PROYECTO_DIR%data\processed\csv" mkdir "%PROYECTO_DIR%data\processed\csv"
if not exist "%PROYECTO_DIR%backups" mkdir "%PROYECTO_DIR%backups"
if not exist "%PROYECTO_DIR%backups\csv" mkdir "%PROYECTO_DIR%backups\csv"

echo ✅ Estructura de directorios creada
echo.

echo 🔍 VERIFICANDO ARCHIVOS NECESARIOS...
echo =====================================

set TODO_OK=1

if exist "%PROYECTO_DIR%urls_etcl_completo.json" (
    echo ✅ urls_etcl_completo.json encontrado
) else (
    echo ⚠️  urls_etcl_completo.json NO encontrado
    echo    Ejecuta: python convert_docx_to_json_enhanced.py
    set TODO_OK=0
)

if exist "%PROYECTO_DIR%scripts\extractors\config_csv.json" (
    echo ✅ config_csv.json encontrado
) else (
    echo ❌ config_csv.json NO encontrado
    set TODO_OK=0
)

echo.

if %TODO_OK%==1 (
    echo ===============================================
    echo ✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE
    echo ===============================================
    echo.
    echo 🚀 PRÓXIMOS PASOS:
    echo.
    echo 1. Para descargar todos los CSVs:
    echo    cd scripts\extractors
    echo    python ejecutar_descarga_masiva.py
    echo.
    echo 2. O usa el batch:
    echo    scripts\extractors\descarga_masiva.bat
    echo.
) else (
    echo ===============================================
    echo ⚠️  CONFIGURACIÓN INCOMPLETA
    echo ===============================================
    echo.
    echo Por favor, revisa los archivos faltantes
    echo.
)

echo Presiona cualquier tecla para salir...
pause >nul
