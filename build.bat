@echo off
echo [1/3] Sanal ortam kontrol ediliyor...
if not exist "venv" (
    python -m venv venv
)
call .\venv\Scripts\activate

echo [2/3] Bagimliliklar guncelleniyor...
pip install -r requirements.txt

echo [3/3] EXE olusturuluyor (Time Reporter.exe)...
pyinstaller --noconsole --onefile --icon=icon.ico --name="Time Reporter" --collect-all customtkinter --add-data "icon.ico;." --add-data "Time Reporter.png;." main.py

echo.
echo Islem tamam! "dist" klasoru icindeki "Time Reporter.exe" dosyasini kullanabilirsiniz.
pause
