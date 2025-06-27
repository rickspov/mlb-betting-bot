@echo off
echo Iniciando MLB Betting Bot Dashboard...
echo.

REM Navegar al directorio del proyecto
cd /d "C:\Users\rianr\Desktop\MLBBETTINGBOT"

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Navegar al directorio dashboard
cd dashboard

REM Ejecutar Streamlit usando la ruta completa
echo Ejecutando dashboard en http://localhost:8501
echo Presiona Ctrl+C para detener
echo.
"..\venv\Scripts\streamlit.exe" run app.py

pause 