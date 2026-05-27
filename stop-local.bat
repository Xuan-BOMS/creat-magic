@echo off
setlocal

set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5175"

call :stop_port %FRONTEND_PORT% Frontend
call :stop_port %BACKEND_PORT% Backend

echo.
echo Local magic services are stopped.
echo.
pause
exit /b

:stop_port
set "FOUND="
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%~1 .*LISTENING"') do (
  if not "%%P"=="0" (
    echo Stopping %~2 on port %~1, PID %%P
    taskkill /PID %%P /T /F >nul 2>&1
    set "FOUND=1"
  )
)
if not defined FOUND echo %~2 is not running on port %~1.
exit /b
