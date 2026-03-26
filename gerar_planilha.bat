@echo off
chcp 65001 >nul
cd /d "%~dp0"
title XMLLite - Gerar planilha XLSX

if not exist "venv\Scripts\python.exe" (
    echo Execute primeiro o arquivo: instalar.bat
    echo.
    pause
    exit /b 1
)

call "%~dp0venv\Scripts\activate.bat"

echo Gerando relatorio_nfse.xlsx a partir da pasta XMLs...
echo.

python "%~dp0relatorio_nfse.py"

if errorlevel 1 (
    echo.
    echo [ERRO] Verifique se a pasta XMLs existe e contem arquivos .xml
) else (
    echo.
    echo Planilha salva nesta pasta: relatorio_nfse.xlsx
)
echo.
pause
