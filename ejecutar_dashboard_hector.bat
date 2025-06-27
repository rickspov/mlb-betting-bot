@echo off
REM Script para ejecutar el dashboard MLB Betting Bot (versión Héctor)

REM Cambiar a la carpeta del proyecto (ajusta la ruta si es necesario)
cd /d %~dp0

REM Ejecutar el dashboard con Streamlit
call streamlit run dashboard/app.py

pause 