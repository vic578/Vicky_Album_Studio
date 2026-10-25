@echo off
cd /d %~dp0
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name VickyAlbumStudioClassic app.py
if errorlevel 1 pause
 echo.
echo Build complete. Check dist\VickyAlbumStudioClassic.exe
pause
