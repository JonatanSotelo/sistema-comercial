@echo off
title Parando Sistema Comercial
color 0C

echo.
echo ========================================
echo    PARANDO SISTEMA COMERCIAL
echo ========================================
echo.

echo 1. Deteniendo contenedores...
docker stop sc_postgres sc_redis 2>nul
docker rm sc_postgres sc_redis 2>nul

echo.
echo 2. Deteniendo procesos de Python (Backend)...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul

echo.
echo 3. Deteniendo procesos de Node.js (Frontend)...
taskkill /f /im node.exe 2>nul

echo.
echo ========================================
echo    SISTEMA DETENIDO
echo ========================================
echo.
pause


