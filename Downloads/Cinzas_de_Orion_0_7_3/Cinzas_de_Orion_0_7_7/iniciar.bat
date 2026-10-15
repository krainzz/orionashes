@echo off
chcp 65001 >nul
title Cinzas de Orion 0.7.7
cd /d "%~dp0"
echo ==========================================================
echo   CINZAS DE ORION 0.7.7 - INICIALIZADOR AUTOMATICO
echo ==========================================================
echo Verificando requerimentos (pygame, moderngl)...
where python >nul 2>nul
if %errorlevel% equ 0 (
    python -m pip install -r requirements.txt >nul 2>nul
    python main.py
) else (
    py -3 -m pip install -r requirements.txt >nul 2>nul
    py -3 main.py
)
if %errorlevel% neq 0 pause
