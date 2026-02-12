@echo off
cd /d %~dp0
if not exist "venv" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    call .\venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .\venv\Scripts\activate
)
echo Starting Time Reporter...
python main.py
pause
