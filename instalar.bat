@echo off
chcp 65001 >nul
cd /d "%~dp0"
title XMLLite - Instalacao

echo ========================================
echo   XMLLite - Instalacao das dependencias
echo ========================================
echo.
echo Pasta do projeto: %~dp0
echo.

if exist "venv\Scripts\python.exe" goto :have_venv

echo Criando ambiente virtual em "venv"...
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 -m venv venv
    goto :check_venv
)
where python >nul 2>&1
if %errorlevel%==0 (
    python -m venv venv
    goto :check_venv
)

echo [ERRO] Python nao encontrado.
echo        Instale em https://www.python.org/downloads/windows/
echo        Marque "Add python.exe to PATH" e abra de novo este arquivo.
echo.
pause
exit /b 1

:check_venv
if not exist "venv\Scripts\python.exe" (
    echo [ERRO] Falha ao criar o ambiente virtual.
    pause
    exit /b 1
)
echo.

:have_venv
set "VPY=%~dp0venv\Scripts\python.exe"

echo Atualizando pip...
"%VPY%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERRO] Falha ao atualizar o pip.
    pause
    exit /b 1
)

echo.
echo Instalando pacotes ^(requirements.txt^)...
"%VPY%" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Concluido com sucesso.
echo   Use executar.bat para abrir o painel web.
echo ========================================
echo.
pause
