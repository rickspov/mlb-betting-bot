@echo off
cd /d "C:\Users\rianr\Desktop\MLBBETTINGBOT"
venv\Scripts\activate.bat
cd dashboard
venv\Scripts\streamlit.exe run app.py
pause 