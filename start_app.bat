@echo off
echo Starting Invoice Validator Application...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /c "cd backend && py -3.10 -m uvicorn main:app --reload"

echo Starting Frontend Server...
start "Frontend Server" cmd /c "cd frontend && npm start"

echo.
echo Application started! You can access it at:
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo.
echo Press any key to close all servers...
pause>nul

taskkill /FI "WindowTitle eq Backend Server*" /F
taskkill /FI "WindowTitle eq Frontend Server*" /F 