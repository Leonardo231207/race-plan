@echo off
cd ..\src
pyinstaller --onefile --windowed --name RacePlan screensaver_scr.py
rename dist\RacePlan.exe RacePlan.scr
copy dist\RacePlan.scr ..\RacePlan.scr
echo Listo
pause
