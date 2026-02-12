@echo off
echo [1/3] Sanal ortam kontrol ediliyor...
if not exist "venv" (
    python -m venv venv
)
call .\venv\Scripts\activate

echo [2/3] Bagimliliklar guncelleniyor...
pip install -r requirements.txt

echo [3/3] EXE olusturuluyor (Terminal acilmayan model)...
:: --noconsole: Terminal penceresini gizler
:: --onefile: Tum projeyi tek bir exe yapar
:: --collect-all customtkinter: CustomTkinter dosyalarini otomatik paketler
pyinstaller --noconsole --onefile --collect-all customtkinter main.py

echo.
echo Islem tamam! "dist" klasoru icindeki main.exe dosyasini kullanabilirsiniz.
pause
