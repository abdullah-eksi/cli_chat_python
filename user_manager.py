import hashlib
import jwt
import datetime
import os
from firebase_config import FirebaseConfig
from colorama import Fore, Style, init

# Colorama'yı başlat (Windows için renkli çıktı)
init()

class UserManager:
    def __init__(self):
        self.firebase_config = FirebaseConfig()
        self.auth = self.firebase_config.get_auth()
        self.db = self.firebase_config.get_database()
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    
    def hash_password(self, password):
        """Şifreyi güvenli bir şekilde hashle"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, user_id):
        """JWT token oluştur"""
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token):
        """JWT token'ı doğrula"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, username, email, password):
        """Yeni kullanıcı kayıt et"""
        try:
            # Firebase Authentication ile kullanıcı oluştur
            user = self.auth.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            
            # Kullanıcı bilgilerini veritabanına kaydet
            user_data = {
                'username': username,
                'email': email,
                'created_at': datetime.datetime.now().isoformat(),
                'is_online': False,
                'last_seen': datetime.datetime.now().isoformat()
            }
            
            self.db.child("users").child(user_id).set(user_data)
            
            print(f"{Fore.GREEN}✅ Kullanıcı başarıyla kaydedildi!{Style.RESET_ALL}")
            return True, user_id
            
        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg:
                print(f"{Fore.RED}❌ Bu e-posta adresi zaten kullanılıyor!{Style.RESET_ALL}")
            elif "WEAK_PASSWORD" in error_msg:
                print(f"{Fore.RED}❌ Şifre çok zayıf! En az 6 karakter olmalı.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Kayıt hatası: {error_msg}{Style.RESET_ALL}")
            return False, None
    
    def login_user(self, email, password):
        """Kullanıcı girişi yap"""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            user_id = user['localId']
            
            # Kullanıcının online durumunu güncelle
            self.db.child("users").child(user_id).update({
                'is_online': True,
                'last_seen': datetime.datetime.now().isoformat()
            })
            
            # Kullanıcı bilgilerini al
            user_data = self.db.child("users").child(user_id).get().val()
            
            print(f"{Fore.GREEN}✅ Hoş geldin, {user_data['username']}!{Style.RESET_ALL}")
            return True, user_id, user_data['username']
            
        except Exception as e:
            error_msg = str(e)
            if "INVALID_EMAIL" in error_msg:
                print(f"{Fore.RED}❌ Geçersiz e-posta adresi!{Style.RESET_ALL}")
            elif "EMAIL_NOT_FOUND" in error_msg:
                print(f"{Fore.RED}❌ Bu e-posta adresi kayıtlı değil!{Style.RESET_ALL}")
            elif "INVALID_PASSWORD" in error_msg:
                print(f"{Fore.RED}❌ Yanlış şifre!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Giriş hatası: {error_msg}{Style.RESET_ALL}")
            return False, None, None
    
    def logout_user(self, user_id):
        """Kullanıcı çıkışı yap"""
        try:
            self.db.child("users").child(user_id).update({
                'is_online': False,
                'last_seen': datetime.datetime.now().isoformat()
            })
            print(f"{Fore.YELLOW}👋 Çıkış yapıldı. Görüşürüz!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Çıkış hatası: {e}{Style.RESET_ALL}")
    
    def get_online_users(self):
        """Online kullanıcıları getir"""
        try:
            users = self.db.child("users").get().val()
            online_users = []
            
            if users:
                for user_id, user_data in users.items():
                    if user_data.get('is_online', False):
                        online_users.append({
                            'id': user_id,
                            'username': user_data['username']
                        })
            
            return online_users
        except Exception as e:
            print(f"{Fore.RED}❌ Online kullanıcılar alınamadı: {e}{Style.RESET_ALL}")
            return []