@echo off
REM Change the following paths
REM Activate Python environment
call "D:/LabAPI/.venv/Scripts/activate.bat"

REM Change working directory to LabAPI root folder and run the Waitress server
cd /d D:/LabAPI/src/
start pythonw run_server.py

REM Change working directory to nginx and run it
cd /d C:/nginx/
start nginx.exe
REM Close cmd window
exit