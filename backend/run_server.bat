@echo off
cd /d %~dp0
py -3.10 -m uvicorn main:app --reload
pause 