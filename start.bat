@echo off
set "PYTHON=%~dp0venv\Scripts\python.exe"
set "MAIN=%~dp0main.py"

if not exist "%PYTHON%" (
    echo Python del virtual environment non trovato: "%PYTHON%"
    exit /b 1
)

"%PYTHON%" "%MAIN%"