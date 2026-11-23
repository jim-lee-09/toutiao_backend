@echo off
title Redis Server
cd /d "C:\Users\Jim\AppData\Local\Microsoft\WinGet\Packages\taizod1024.redis-windows-fork_Microsoft.Winget.Source_8wekyb3d8bbwe\Redis-8.10.2-Windows-x64-msys2"
echo Starting Redis... close this window to stop it.
redis-server.exe redis.conf
echo.
echo Redis stopped. Press any key to close.
pause >nul
