@echo off
set input_args=%*

REM Run the Intel oneAPI environment setup
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" --force

REM Pass all arguments to PowerShell as a single string to handle special characters
powershell -Command "Start-Process powershell -ArgumentList './tools/run_pixi.ps1 \"%input_args%\"' -NoNewWindow -Wait"
