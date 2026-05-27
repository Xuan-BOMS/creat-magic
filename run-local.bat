@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5175"

call :is_port_listening %BACKEND_PORT%
if "%PORT_LISTENING%"=="1" (
  echo Backend already listening on port %BACKEND_PORT%.
) else (
  echo Starting backend on http://127.0.0.1:%BACKEND_PORT%
  start "Magic Backend" /D "%ROOT%backend" cmd /c python -m uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT%
)

call :is_port_listening %FRONTEND_PORT%
if "%PORT_LISTENING%"=="1" (
  echo Frontend already listening on port %FRONTEND_PORT%.
) else (
  echo Starting frontend on http://127.0.0.1:%FRONTEND_PORT%
  start "Magic Frontend" /D "%ROOT%frontend" cmd /c npm run dev -- --host 127.0.0.1 --port %FRONTEND_PORT%
)

echo.
echo Frontend: http://127.0.0.1:%FRONTEND_PORT%
echo Backend:  http://127.0.0.1:%BACKEND_PORT%
echo.
echo The browser will open after a short startup wait.
timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:%FRONTEND_PORT%"
echo.
pause
exit /b

:is_port_listening
set "PORT_LISTENING=0"
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%~1 .*LISTENING"') do set "PORT_LISTENING=1"
exit /b
