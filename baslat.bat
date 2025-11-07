@echo off
title VPN Baslatici
color 0A


net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)


cd /d "%~dp0"

cls



python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python yuklu degil!
    pause
    exit /b 1
)

echo [+] Python: TAMAM
echo.

:: dosyalar klasorune gec
if not exist "dosyalar" (
    echo [!] dosyalar klasoru bulunamadi!
    pause
    exit /b 1
)

cd dosyalar


echo [*] Paketler kontrol ediliyor...
python -m pip install --upgrade pip winotify pywin32 pillow

echo.
echo [+] Hazir!
echo.


if exist "erisimasan.py" (
    echo [*] VPN baslatiliyor...
    timeout /t 2 /nobreak >nul
    start /B pythonw erisimasan.py
    exit
) else (
    echo [!] erisimasan.py bulunamadi!
    pause
)

cd ..