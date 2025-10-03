# CliChat - Komut Satırı Chat Uygulaması

Firebase tabanlı gerçek zamanlı komut satırı chat uygulaması.

## Özellikler

- 🔐 Kullanıcı kaydı ve girişi
- 💬 Gerçek zamanlı mesajlaşma
- 🏠 Chat odası oluşturma ve katılma
- 👥 Online kullanıcı takibi
- 🎨 Renkli terminal arayüzü
- 📱 JWT token tabanlı oturum yönetimi

## Gereksinimler

- Python 3.7+
- Firebase projesi
- İnternet bağlantısı

## Kurulum

1. Repository'yi klonlayın veya indirin

2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

3. `.env` dosyasını Firebase Console bilgilerinizle güncelleyin:

```bash
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your_project.firebaseio.com
# ... diğer Firebase bilgileri
```

## Kullanım

Uygulamayı çalıştırmak için:

```bash
python main.py
```

### Ana Menü Seçenekleri

1. **Kayıt Ol** - Yeni kullanıcı hesabı oluştur
2. **Giriş Yap** - Mevcut hesapla giriş yap
3. **Çıkış** - Uygulamadan çık

### Chat Menüsü

1. **Oda Oluştur** - Yeni chat odası oluştur
2. **Odaya Katıl** - Mevcut odaya katıl (6 haneli ID ile)
3. **Odaları Listele** - Aktif odaları görüntüle
4. **Online Kullanıcılar** - Çevrimiçi kullanıcıları gör
5. **Çıkış Yap** - Hesaptan çık

### Chat Komutları

- Mesaj yazmak için doğrudan metin girin
- `/quit` - Odadan ayrıl
- Gerçek zamanlı mesaj alımı otomatik olarak çalışır


## Teknolojiler

- **Python** - Ana programlama dili
- **Firebase** - Gerçek zamanlı veritabanı ve authentication
- **PyRebase** - Firebase Python SDK
- **Colorama** - Terminal renklendirme
- **JWT** - Token tabanlı oturum yönetimi
- **PyInstaller** - Executable dosya oluşturma

## Proje Yapısı

```text
├── main.py              # Ana uygulama
├── user_manager.py      # Kullanıcı yönetimi
├── chat_manager.py      # Chat odası yönetimi
├── firebase_config.py   # Firebase yapılandırması
├── requirements.txt     # Python bağımlılıkları
├── .env                 # Ortam değişkenleri
└── README.md           # Bu dosya
```



## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Sorularınız için issue açabilir veya pull request gönderebilirsiniz.
