@echo off
REM Script para actualizar la app MLB Betting Bot (versión Héctor)

REM Cambiar a la carpeta del proyecto (ajusta la ruta si es necesario)
cd /d %~dp0

REM Actualizar el repositorio
call git pull

REM Instalar/actualizar dependencias
call pip install -r requirements.txt

pause 