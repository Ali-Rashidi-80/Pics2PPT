@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo ===================================================
echo   Pics2PPT - Portable EXE
echo ===================================================
echo.

if not exist "pics2ppt_entry.py" (
    echo [ERROR] pics2ppt_entry.py missing
    pause & exit /b 1
)

if not exist "icon.ico" (
    echo [WARN] icon.ico missing — EXE will use default icon
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause & exit /b 1
)

echo [1/5] Installing dependencies...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] pip install failed
    pause & exit /b 1
)

echo [2/5] UPX (optional compression)...
set "UPX_DIR="
if exist "tools\upx\upx.exe" set "UPX_DIR=%ROOT%tools\upx"
where upx >nul 2>&1
if not errorlevel 1 if not defined UPX_DIR (
    for /f "delims=" %%U in ('where upx 2^>nul') do set "UPX_DIR=%%~dpU"
    if defined UPX_DIR set "UPX_DIR=!UPX_DIR:~0,-1!"
)
if not defined UPX_DIR (
    echo UPX not found - downloading to tools\upx...
    if not exist "tools" mkdir "tools"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$u='https://github.com/upx/upx/releases/download/v4.2.4/upx-4.2.4-win64.zip';" ^
        "$z='%ROOT%tools\upx.zip'; $d='%ROOT%tools\upx_tmp';" ^
        "Invoke-WebRequest -Uri $u -OutFile $z -UseBasicParsing;" ^
        "Expand-Archive -Path $z -DestinationPath $d -Force;" ^
        "$exe=Get-ChildItem $d -Recurse -Filter upx.exe | Select-Object -First 1;" ^
        "New-Item -ItemType Directory -Force -Path '%ROOT%tools\upx' | Out-Null;" ^
        "Copy-Item $exe.FullName '%ROOT%tools\upx\upx.exe' -Force;" ^
        "Remove-Item $z -Force; Remove-Item $d -Recurse -Force"
    if exist "tools\upx\upx.exe" set "UPX_DIR=%ROOT%tools\upx"
)
if defined UPX_DIR ( echo UPX: !UPX_DIR! ) else ( echo [WARN] UPX unavailable - building without extra compression )

echo [3/5] Cleaning old build...
if exist "build\Pics2PPT.portable" rmdir /s /q "build\Pics2PPT.portable"
if exist "dist\Pics2PPT.exe" del /f /q "dist\Pics2PPT.exe"
if exist "dist\Pics2PPT" rmdir /s /q "dist\Pics2PPT"

echo [4/5] PyInstaller...
set "UPX_ARG="
if defined UPX_DIR set "UPX_ARG=--upx-dir \"!UPX_DIR!\""

python -m PyInstaller --noconfirm --clean !UPX_ARG! Pics2PPT.portable.spec
if errorlevel 1 (
    echo [ERROR] Build failed
    pause & exit /b 1
)

echo [5/5] Verify single-file EXE...
if not exist "dist\Pics2PPT.exe" (
    echo [ERROR] dist\Pics2PPT.exe not found
    pause & exit /b 1
)
for /d %%D in ("dist\*") do (
    echo [ERROR] Expected one EXE only, found folder: %%D
    pause & exit /b 1
)

for %%A in ("dist\Pics2PPT.exe") do set "SZ=%%~zA"
set /a "SZMB=!SZ!/1048576"
echo.
echo SUCCESS: dist\Pics2PPT.exe  (single portable file, ~!SZMB! MB)
echo.
pause
