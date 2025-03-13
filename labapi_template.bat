@echo off
REM Kill server if running
call taskkill /f /im pythonw.exe
call taskkill /f /im nginx.exe

REM Change the following paths
REM Activate Python environment
call "D:/path-to-LabAPI/.venv/Scripts/activate.bat"

REM Change working directory to LabAPI root folder and run the Waitress server
cd /d D:/path-to-LabAPI/src/
start pythonw run_server.py

REM Change working directory to nginx and run it
cd /d C:/path-to-nginx/
start nginx.exe
REM Close cmd window
exit