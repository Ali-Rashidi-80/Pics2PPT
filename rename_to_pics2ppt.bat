@echo off
chcp 65001 >nul
echo.
echo اگر هنوز پوشه D:\0\gen_powerpoint وجود دارد و Cursor بسته است:
echo   1) این فایل را از D:\0\Pics2PPT اجرا نکنید.
echo   2) Cursor را ببندید.
echo   3) در PowerShell اجرا کنید:
echo      Remove-Item -Recurse -Force "D:\0\gen_powerpoint"
echo   4) Cursor را با پوشه D:\0\Pics2PPT باز کنید.
echo.
pause
