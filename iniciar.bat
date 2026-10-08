@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem Cinzas de Orion: o Pygame e demais dependencias sao mantidos fora da
rem pasta da versao, em %LOCALAPPDATA%, para serem reutilizados por novas versoes.
set "GAME_DATA=%LOCALAPPDATA%\CinzasDeOrion"
set "GAME_DEPS=%GAME_DATA%\deps"

rem 1) Preferir um Python do sistema que ja tenha Pygame.
where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import pygame" >nul 2>&1
    if not errorlevel 1 (
        py -3 main.py
        if errorlevel 1 goto error
        exit /b 0
    )
)

where python >nul 2>&1
if not errorlevel 1 (
    python -c "import pygame" >nul 2>&1
    if not errorlevel 1 (
        python main.py
        if errorlevel 1 goto error
        exit /b 0
    )
)

rem 2) Reutilizar uma instalacao persistente compartilhada entre versoes.
if not exist "%GAME_DEPS%" mkdir "%GAME_DEPS%" >nul 2>&1
if not exist "%GAME_DEPS%" goto error_deps

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -m pip --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_RUN=py -3"
        goto persistent_python_ready
    )
)

where python >nul 2>&1
if not errorlevel 1 (
    python -m pip --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_RUN=python"
        goto persistent_python_ready
    )
)

echo Python 3 nao foi encontrado.
echo Instale Python 3.11+ em https://www.python.org/downloads/ e tente novamente.
pause
exit /b 1

:persistent_python_ready
set "PYTHONPATH=%GAME_DEPS%;%PYTHONPATH%"

rem Se o Pygame ja estiver na pasta persistente, nao instala novamente.
%PYTHON_RUN% -c "import pygame; print(pygame.version.ver)" >nul 2>&1
if not errorlevel 1 goto run_persistent

echo Preparando o ambiente compartilhado do jogo pela primeira vez...
echo Instalando Pygame uma vez em:
echo %GAME_DEPS%
%PYTHON_RUN% -m pip install --disable-pip-version-check --upgrade --force-reinstall --target "%GAME_DEPS%" -r requirements.txt
if errorlevel 1 goto install_error

%PYTHON_RUN% -c "import pygame; print(pygame.version.ver)" >nul 2>&1
if errorlevel 1 goto install_error

goto run_persistent

:run_persistent
%PYTHON_RUN% main.py
if errorlevel 1 goto error
exit /b 0

:error_deps
echo Nao foi possivel criar a pasta persistente do jogo:
echo %GAME_DEPS%
pause
exit /b 1

:install_error
echo.
echo Nao foi possivel instalar o Pygame.
echo Verifique sua conexao com a internet e se o Python possui pip habilitado.
pause
exit /b 1

:error
echo.
echo Nao foi possivel iniciar o jogo. Copie a mensagem de erro acima.
pause
exit /b 1
