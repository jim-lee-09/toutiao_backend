@echo off
title Redis CLI
cd /d "C:\Users\Jim\AppData\Local\Microsoft\WinGet\Packages\taizod1024.redis-windows-fork_Microsoft.Winget.Source_8wekyb3d8bbwe\Redis-8.10.2-Windows-x64-msys2"
echo Redis CLI ready. Try: KEYS *   GET news:categories   TTL news:categories
redis-cli.exe
