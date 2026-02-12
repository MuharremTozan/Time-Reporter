# Time Reporter - Proje Durum Raporu (Şubat 2026)

Bu belge, yerel zaman takip uygulaması olan **Time Reporter** projesinin mevcut teknik durumunu ve tamamlanan özelliklerini özetler.

## ✅ Tamamlanan Özellikler

### 1. Mimari Tasarım
- **Dil:** Python 3.10+
- **Veritabanı:** SQLite (Yerel dosya tabanlı saklama).
- **Klasör Yapısı:** Modüler yapı (`src/core`, `src/db`, `src/utils`) oluşturuldu ve Python paket standartlarına (`__init__.py`) uygun hale getirildi.

### 2. Takip Motoru (Core Engine) - *Pro Seviye*
- **Hibrit Takip Modeli:** 
    - **Sinyal Tabanlı (Event-driven):** Windows `WinEventHook` kullanılarak pencere değişimleri milisaniye hassasiyetinde yakalanıyor.
    - **Kalp Atışı (Heartbeat):** Pencere değişmese bile her 60 saniyede bir mevcut bloğun süresi güncelleniyor.
- **Çoklu İş Parçacığı (Multi-threading):** Windows mesaj pompası (PumpMessages) ve zamanlayıcı ayrı thread'lerde çalışarak %0'a yakın CPU kullanımı sağlıyor.

### 3. Veri Yönetimi
- **Blok Bazlı Kayıt:** Her dakika yeni satır eklemek yerine, aynı uygulama kullanıldığı sürece mevcut bloğun süresi artırılıyor (Time-blocking).
- **Otomatik Şema:** Uygulama ilk açıldığında SQLite tablosunu (`activity_blocks`) otomatik olarak oluşturuyor.

### 4. Akıllı Özellikler
- **Boşta Kalma (Idle) Tespiti:** Kullanıcı 5 dakika boyunca bilgisayarda işlem yapmazsa takip otomatik olarak durduruluyor.
- **Proses Çözümleme:** Pencere başlığının ötesinde, arka planda çalışan gerçek `.exe` adı (örn: `chrome.exe`) tespit edilerek gruplandırma temeli atıldı.

### 5. Kullanılabilirlik
- **run.bat:** Kullanıcının terminalle uğraşmadan, çift tıklayarak sanal ortamı (venv) kurmasını ve uygulamayı başlatmasını sağlayan otomasyon dosyası.
- **Loglama:** Tüm işlemler zaman damgalı olarak terminale ve sistem loglarına basılıyor.

## 📂 Proje Yapısı
```text
/Time-Reporter
├── main.py              # Uygulama giriş noktası
├── run.bat              # Windows başlatıcı
├── time_reporter.db     # Veritabanı (çalışma anında oluşur)
├── requirements.txt     # Bağımlılıklar
├── AGENTS.md            # Geliştirici rehberi
├── documentation/       # Raporlar ve dokümanlar
└── src/
    ├── core/            # Tracker ve Engine mantığı
    ├── db/              # Veritabanı yöneticisi
    ├── utils/           # Idle tespiti vb. yardımcılar
    └── ui/              # (Yapım aşamasında) Arayüz bileşenleri
```

## 🚀 Sonraki Adımlar
- [ ] **UI Geliştirme:** CustomTkinter ile modern bir dashboard tasarımı.
- [ ] **Görselleştirme:** Toplanan verilerin grafiklerle (pasta/çubuk grafik) gösterilmesi.
- [ ] **Gruplandırma:** Uygulamaların kategorilere ayrılması (İş, Eğlence, Sosyal Medya).
