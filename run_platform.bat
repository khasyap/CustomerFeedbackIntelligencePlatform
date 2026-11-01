@echo off
echo ======================================================================
echo Launching Customer Feedback Intelligence and Sentiment Analytics Platform
echo ======================================================================
echo.
echo Starting unified FastAPI backend and React Web Dashboard on port 8000...
echo Web Dashboard: http://localhost:8000/
echo Swagger Docs:  http://localhost:8000/docs
echo API Health:    http://localhost:8000/api/health
echo.
echo Press CTRL+C to stop the platform.
echo ======================================================================
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause

