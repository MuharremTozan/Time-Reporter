# Time Reporter - Proje Durum Raporu (Şubat 2026)

Bu belge, yerel zaman takip uygulaması olan **Time Reporter** projesinin mevcut teknik durumunu ve tamamlanan özelliklerini özetler.

## ✅ Tamamlanan Özellikler

### 1. Mimari Tasarım
- **Dil:** Python 3.10+
- **Veritabanı:** SQLite (Yerel dosya tabanlı saklama).
- **Arayüz:** CustomTkinter tabanlı modern ve karanlık tema odaklı UI.
- **Klasör Yapısı:** Modüler yapı (`src/core`, `src/db`, `src/ui`, `src/utils`) oluşturuldu.

### 2. Takip Motoru (Core Engine)
- **Hibrit Takip Modeli:** 
    - **Sinyal Tabanlı:** Pencere değişimleri Windows Hook'ları ile anlık yakalanıyor.
    - **Heartbeat:** 60 saniyelik periyotlarla aktif bloğun süresi güncelleniyor.
- **Çoklu İş Parçacığı:** Engine, Tray ve UI ayrı thread'lerde çalışarak donmaları engeller.

### 3. Kullanıcı Arayüzü (UI/UX)
- **Dashboard:** Canlı takip kartı ve son 15 aktivite bloğunun listesi.
- **İstatistikler:** Matplotlib entegrasyonu ile Uygulama ve Kategori bazlı pasta grafikler.
- **Tarih Filtreleme:** İstatistikler için "Bugün", "Son 7 Gün" ve "Son 30 Gün" seçenekleri.
- **Kategori Yönetimi:** Uygulamaları "Development", "Browsing", "Work" gibi kategorilere atama ekranı.

### 4. Sistem ve Arka Plan Entegrasyonu
- **System Tray (Sistem Tepsisi):** Uygulama kapatıldığında kapanmaz, tepsiye küçülür. Sağ tık menüsü ile yönetilebilir.
- **Auto-startup:** Windows açıldığında otomatik başlama seçeneği (Registry entegrasyonu).
- **Akıllı Boşta Kalma Tespiti:** 5 dakika işlem yapılmazsa takibi durdurur.

### 5. Raporlama ve Dışa Aktarma
- **Otomatik Export:** Uygulama kapandığında o günün verilerini otomatik olarak metin dosyasına yazar.
- **Akıllı Format:** Ardışık aynı aktiviteler birleştirilir ve aradaki molalar (`- break`) otomatik tespit edilir.
- **Konum:** Raporlar uygulamanın (veya EXE'nin) yanındaki `Exports/` klasöründe saklanır.

## 📂 Proje Yapısı
```text
/Time-Reporter
├── main.py              # Uygulama giriş noktası
├── build.bat            # EXE oluşturma betiği
├── run.bat              # Geliştirme modu başlatıcı
├── requirements.txt     # Bağımlılıklar
└── src/
    ├── core/            # Tracker ve Engine mantığı
    ├── db/              # SQLite veritabanı yönetimi
    ├── ui/              # CustomTkinter arayüzleri
    └── utils/           # Tray, Startup, Export ve Idle yardımcıları
```

## 🚀 Sonraki Adımlar
- [ ] **Gelişmiş Filtreleme:** Özel tarih aralığı seçici.
- [ ] **Veri Temizleme:** Belirli bir tarihten eski kayıtları silme seçeneği.
- [ ] **Kategori Ekleme:** Kullanıcının kendi özel kategorilerini oluşturabilmesi.
