@echo off
echo ========================================
echo  INSTALADOR DE DEPENDENCIAS - RACE PLAN
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    echo Descarga Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python encontrado
python --version
echo.

REM Crear entorno virtual si no existe
if not exist "venv\" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
) else (
    echo [INFO] Entorno virtual ya existe
)
echo.

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado
echo.

REM Actualizar pip
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias
echo [INFO] Instalando dependencias desde requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Error al instalar dependencias
    pause
    exit /b 1
)
echo.
echo ========================================
echo  INSTALACION COMPLETA
echo ========================================
echo.
echo Para activar el entorno virtual manualmente:
echo   venv\Scripts\activate.bat
echo.
echo Para ejecutar el lector:
echo   python lector.py
echo.
echo Para probar el salvapantallas (preview):
echo   python screensaver_preview.py
echo.
pause
