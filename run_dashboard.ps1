Write-Host "Iniciando MLB Betting Bot Dashboard..." -ForegroundColor Green
Write-Host ""

# Navegar al directorio del proyecto
Set-Location "C:\Users\rianr\Desktop\MLBBETTINGBOT"

# Activar entorno virtual
& "venv\Scripts\Activate.ps1"

# Navegar al directorio dashboard
Set-Location "dashboard"

# Ejecutar Streamlit usando la ruta completa
Write-Host "Ejecutando dashboard en http://localhost:8501" -ForegroundColor Yellow
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

& "..\venv\Scripts\streamlit.exe" run app.py

Read-Host "Presiona Enter para salir" 