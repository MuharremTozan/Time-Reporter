# Time Reporter - Local Time Tracking App

Bu uygulama, kullanıcının Windows üzerinde hangi pencerede ne kadar vakit geçirdiğini otomatik olarak takip eden ve yerel bir veritabanında raporlayan bir masaüstü uygulamasıdır.

## Neden Python?
- **Düşük Kaynak Tüketimi:** Electron gibi ağır frameworkler yerine sistem kaynaklarını minimal tüketen bir yapı tercih edildi.
- **Native API Erişimi:** Windows Win32 API'lerine `pywin32` ile doğrudan ve kolay erişim.
- **Hızlı Prototipleme:** Veri işleme ve SQLite entegrasyonu için ideal.

## Proje Yol Haritası

### Faz 1: Altyapı ve Takip (Background Engine)
- [ ] Proje ortamının hazırlanması (Virtualenv, dependencies).
- [ ] SQLite veritabanı şemasının tasarımı (Sessions, Windows, Activities).
- [ ] Arka planda aktif pencereyi ve uygulama adını yakalayan `tracker` modülünün yazılması.
- [ ] Boşta kalma (Idle time) tespiti (Klavye/Mouse hareket yoksa takibi durdurma).

### Faz 2: Veri Yönetimi
- [ ] Verilerin periyodik olarak SQLite'a kaydedilmesi.
- [ ] Uygulama gruplandırma mantığı (Örn: `chrome.exe` altındaki "YouTube" ve "Gmail" başlıklarını ayırt etme veya birleştirme).

### Faz 3: Arayüz (Frontend - Desktop UI)
- [ ] `CustomTkinter` veya `PyQt6` kullanarak ana dashboard tasarımı.
- [ ] Günlük/Haftalık zaman bloklarını gösteren grafiksel raporlar.
- [ ] Sistem tepsisi (System Tray) entegrasyonu (Uygulamanın arka planda görünmez çalışması).

### Faz 4: Paketleme
- [ ] Uygulamanın `.exe` haline getirilmesi.
- [ ] Başlangıçta çalıştırma (Startup) ayarı.

## Teknik Yığın (Tech Stack)
- **Dil:** Python 3.x
- **Veritabanı:** SQLite
- **Kütüphaneler:** `pywin32`, `customtkinter`, `pandas` (raporlama için), `pyinstaller`
