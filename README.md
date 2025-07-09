# 📧 Firebase E-posta Gönderici

Terminal üzerinden Firebase entegrasyonlu e-posta gönderme uygulaması.

## 🚀 Özellikler

- ✅ Terminal üzerinden kolay kullanım
- ✅ Firebase ile e-posta logları
- ✅ Gmail API entegrasyonu
- ✅ E-posta doğrulama
- ✅ Gönderim geçmişi
- ✅ Renkli terminal çıktıları
- ✅ Docker desteği

## 📋 Gereksinimler

- Python 3.9+
- macOS (diğer işletim sistemlerinde de çalışır)
- Google Cloud hesabı
- Firebase projesi

## 🛠️ Kurulum

### 1. Projeyi Klonlayın

```bash
git clone <repo-url>
cd email-sender-firebase
```

### 2. Virtual Environment Oluşturun

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Firebase Kurulumu

1. [Firebase Console](https://console.firebase.google.com)'a gidin
2. Yeni proje oluşturun veya mevcut projeyi seçin
3. Proje Ayarları > Servis Hesapları > Yeni özel anahtar oluştur
4. JSON dosyasını `config/firebase_config.json` olarak kaydedin

### 5. Gmail API Kurulumu

1. [Google Cloud Console](https://console.cloud.google.com)'a gidin
2. Gmail API'yi etkinleştirin
3. OAuth 2.0 Client ID oluşturun (Desktop app)
4. JSON dosyasını `config/gmail_credentials.json` olarak kaydedin

### 6. Çevre Değişkenleri

`.env` dosyası oluşturun:

```env
FIREBASE_CONFIG_PATH=config/firebase_config.json
SENDER_EMAIL=your-email@gmail.com
GMAIL_CREDENTIALS_PATH=config/gmail_credentials.json
LOG_LEVEL=INFO
APP_ENV=development
```

## 💻 Kullanım

### İnteraktif Mod

```bash
python -m src.main
```

### Doğrudan E-posta Gönderme

```bash
python -m src.main -e recipient@example.com
```

### Gönderim Geçmişi

```bash
python -m src.main -H
python -m src.main -H -l 20  # Son 20 kayıt
```

## 🧪 Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage ile
pytest --cov=src --cov=utils tests/
```

## 🐳 Docker Kullanımı

### Build

```bash
docker-compose build
```

### Çalıştırma

```bash
docker-compose run --rm email-sender
```

### İnteraktif Shell

```bash
docker-compose run --rm email-sender /bin/bash
```

## 📁 Proje Yapısı

```
email-sender-firebase/
├── src/
│   ├── main.py              # Ana uygulama
│   ├── email_service.py     # Gmail API servisi
│   └── firebase_client.py   # Firebase işlemleri
├── config/
│   └── settings.py          # Yapılandırma
├── utils/
│   ├── validators.py        # E-posta doğrulama
│   └── logger.py            # Loglama
└── tests/                   # Test dosyaları
```

## 🔐 Güvenlik Notları

- `firebase_config.json` ve `gmail_credentials.json` dosyalarını asla Git'e eklemeyin
- `.env` dosyasını güvende tutun
- Production'da farklı Firebase projesi kullanın

## 📝 Lisans

MIT

## 👥 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın