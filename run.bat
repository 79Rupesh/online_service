@echo off
title MP Suvidha - Madhya Pradesh Digital Services
cd /d "%~dp0"
echo =======================================================
echo  MP SUVIDHA: Madhya Pradesh Digital Services
echo  Starting server at http://127.0.0.1:5000
echo =======================================================
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python app.py
pause
