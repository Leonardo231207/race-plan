@echo off
cd /d %~dp0
cd ..\src
echo Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist RacePlan.spec del /q RacePlan.spec
echo Compilando...
python -m PyInstaller --onefile --windowed --name RacePlan screensaver_scr.py
if exist dist\RacePlan.exe (
  if exist RacePlan.scr del /q RacePlan.scr
  ren dist\RacePlan.exe RacePlan.scr
  copy /Y dist\RacePlan.scr ..\RacePlan.scr
  echo Listo - RacePlan.scr generado en la raiz
) else (
  echo No se genero el exe
)
pause
