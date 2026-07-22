@echo off
title AI Campus Placement Prediction System
cd /d "%~dp0"
echo.
echo  ============================================
echo   AI Campus Placement Prediction System
echo   Antigravity-Inspired UI
echo  ============================================
echo.
echo  Starting server...
echo  Opening browser at http://localhost:8501
echo.
start "" http://localhost:8501
python -m streamlit run app.py --server.headless true --server.port 8501 --server.address 0.0.0.0
pause
