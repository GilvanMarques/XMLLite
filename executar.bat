@echo off
chcp 65001 >nul
cd /d "%~dp0"
title XMLLite - Relatorio NFSe

if not exist "venv\Scripts\python.exe" (
    echo Execute primeiro o arquivo: instalar.bat
    echo.
    pause
    exit /b 1
)

call "%~dp0venv\Scripts\activate.bat"

echo ========================================
echo   Relatorio NFSe ^(Streamlit^)
echo ========================================
echo.
echo O navegador deve abrir em http://localhost:8501
echo Para encerrar o servidor: feche esta janela ou Ctrl+C
echo.

python -m streamlit run "%~dp0app_streamlit.py"

echo.
pause
