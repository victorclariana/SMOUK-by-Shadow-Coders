@echo off
rem SMOUK by Shadow Coders - development launcher
set "SMOUK_PYTHON=C:\msys64\mingw64\bin\python.exe"
if not exist "%SMOUK_PYTHON%" set "SMOUK_PYTHON=C:\msys64\mingw64\bin\python3.exe"
if not exist "%SMOUK_PYTHON%" set "SMOUK_PYTHON=C:\msys64\mingw64\bin\python3.14.exe"
if not exist "%SMOUK_PYTHON%" (
    echo SMOUK cannot start: no verified MSYS2 Python interpreter was found.
    exit /b 1
)
"%SMOUK_PYTHON%" "%~dp0run_smouk.py" %*
