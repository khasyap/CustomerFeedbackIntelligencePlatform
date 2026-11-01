Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Launching Customer Feedback Intelligence & Sentiment Analytics Platform" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting unified FastAPI backend and React Web Dashboard on port 8000..." -ForegroundColor Green
Write-Host "Web Dashboard: http://localhost:8000/" -ForegroundColor Yellow
Write-Host "Swagger Docs:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "API Health:    http://localhost:8000/api/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop the platform." -ForegroundColor DarkGray
Write-Host "======================================================================" -ForegroundColor Cyan

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

