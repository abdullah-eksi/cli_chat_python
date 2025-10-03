import os
import pyrebase
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class FirebaseConfig:
    def __init__(self):
        self.config = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID")
        }
        
        # Firebase bağlantısını başlat
        self.firebase = pyrebase.initialize_app(self.config)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()
    
    def get_auth(self):
        return self.auth
    
    def get_database(self):
        return self.db
    
    def verify_config(self):
        """Firebase yapılandırmasının doğruluğunu kontrol et"""
        missing_configs = []
        for key, value in self.config.items():
            if not value or value.startswith("your_"):
                missing_configs.append(key)
        
        if missing_configs:
            print(f"⚠️  Eksik Firebase yapılandırması: {', '.join(missing_configs)}")
            print("Lütfen .env dosyasını Firebase Console'dan aldığınız bilgilerle güncelleyin.")
            return False
        return True