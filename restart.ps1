# Clean restart script - removes Python cache and restarts server
Write-Host 'Cleaning Python cache...' -ForegroundColor Yellow

# Remove __pycache__ directories
Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Remove .pyc files
Get-ChildItem -Path . -Recurse -File -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host 'Cache cleared!' -ForegroundColor Green
Write-Host 'Starting server...' -ForegroundColor Cyan
Write-Host ''

python main.py
