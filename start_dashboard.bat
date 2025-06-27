@echo off
title MLB Betting Bot Dashboard
color 0A

echo ========================================
echo    MLB Betting Bot Dashboard
echo ========================================
echo.

REM Verificar si estamos en el directorio correcto
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: No se encuentra el entorno virtual
    echo Asegurate de estar en el directorio MLBBETTINGBOT
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [1/4] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM Verificar que streamlit esté instalado
echo [2/4] Verificando Streamlit...
venv\Scripts\streamlit.exe --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Streamlit no está instalado
    echo Ejecuta: pip install streamlit
    pause
    exit /b 1
)

REM Navegar al directorio dashboard
echo [3/4] Navegando al dashboard...
cd dashboard
if errorlevel 1 (
    echo ERROR: No se pudo navegar al directorio dashboard
    pause
    exit /b 1
)

REM Ejecutar dashboard
echo [4/4] Iniciando dashboard...
echo.
echo ========================================
echo    Dashboard iniciado exitosamente!
echo    URL: http://localhost:8501
echo    Presiona Ctrl+C para detener
echo ========================================
echo.

venv\Scripts\streamlit.exe run app.py

echo.
echo Dashboard detenido.
pause 