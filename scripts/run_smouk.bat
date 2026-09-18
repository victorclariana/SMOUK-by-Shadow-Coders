@echo off
rem SMOUK by Shadow Coders - development launcher
set "SMOUK_PYTHON=C:\msys64\mingw64\bin\python.exe"
if not exist "%SMOUK_PYTHON%" set "SMOUK_PYTHON=C:\msys64\mingw64\bin\python3.exe"
"%SMOUK_PYTHON%" "%~dp0run_smouk.py" %*
