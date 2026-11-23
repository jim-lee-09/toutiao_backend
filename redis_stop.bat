@echo off
title Stop Redis
taskkill /IM redis-server.exe /F
echo.
echo Redis stop command finished. Press any key to close.
pause >nul
