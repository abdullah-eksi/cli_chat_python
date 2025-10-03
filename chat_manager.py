import datetime
import threading
import time
import random
import sys
from firebase_config import FirebaseConfig
from colorama import Fore, Style, Back

class ChatManager:
    def __init__(self):
        self.firebase_config = FirebaseConfig()
        self.db = self.firebase_config.get_database()
        self.current_room = None
        self.user_id = None
        self.username = None
        self.listening = False
        self.listener_thread = None
        self.last_sent_message_time = None  # Son gönderdiğimiz mesajın zamanını takip et
    
    def generate_room_id(self):
        """6 haneli benzersiz oda ID'si oluştur"""
        max_attempts = 100
        for _ in range(max_attempts):
            # 100000 ile 999999 arasında 6 haneli sayı oluştur
            room_id = str(random.randint(100000, 999999))
            
            # ID'nin kullanılıp kullanılmadığını kontrol et
            existing_room = self.db.child("rooms").child(room_id).get().val()
            if not existing_room:
                return room_id
        
        # Eğer 100 denemede benzersiz ID bulunamazsa timestamp ekle
        return str(random.randint(100000, 999999)) + str(int(datetime.datetime.now().timestamp()))[-3:]

    def create_room(self, room_name, user_id, username):
        """Yeni sohbet odası oluştur"""
        try:
            # Benzersiz 6 haneli ID oluştur
            room_id = self.generate_room_id()
            
            room_data = {
                'name': room_name,
                'created_by': user_id,
                'created_at': datetime.datetime.now().isoformat(),
                'members': {user_id: username},
                'member_count': 1
            }
            
            # Belirlediğimiz ID ile odayı oluştur
            self.db.child("rooms").child(room_id).set(room_data)
            
            print(f"{Fore.GREEN}✅ '{room_name}' odası oluşturuldu! (ID: {room_id}){Style.RESET_ALL}")
            return room_id
            
        except Exception as e:
            print(f"{Fore.RED}❌ Oda oluşturma hatası: {e}{Style.RESET_ALL}")
            return None
    
    def join_room(self, room_id, user_id, username):
        """Sohbet odasına katıl"""
        try:
            # Odanın var olup olmadığını kontrol et
            room_data = self.db.child("rooms").child(room_id).get().val()
            if not room_data:
                print(f"{Fore.RED}❌ Oda bulunamadı!{Style.RESET_ALL}")
                return False
            
            # Kullanıcıyı odaya ekle
            self.db.child("rooms").child(room_id).child("members").child(user_id).set(username)
            
            # Üye sayısını güncelle
            current_members = self.db.child("rooms").child(room_id).child("members").get().val()
            member_count = len(current_members) if current_members else 1
            self.db.child("rooms").child(room_id).update({'member_count': member_count})
            
            self.current_room = room_id
            self.user_id = user_id
            self.username = username
            
            print(f"{Fore.GREEN}✅ '{room_data['name']}' odasına katıldınız!{Style.RESET_ALL}")
            
            # Önceki mesajları göster
            self.show_chat_history()
            
            # Katılım mesajı gönder
            self.send_system_message(f"{username} odaya katıldı! 👋")
            
            print(f"\n{Fore.CYAN}💬 Mesaj yazmaya başlayabilirsiniz. Çıkmak için '/quit' yazın.{Style.RESET_ALL}")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Odaya katılma hatası: {e}{Style.RESET_ALL}")
            return False
    
    def leave_room(self):
        """Sohbet odasından ayrıl"""
        if not self.current_room:
            return
        
        try:
            # Ayrılım mesajı gönder
            self.send_system_message(f"{self.username} odadan ayrıldı! 👋")
            
            # Kullanıcıyı odadan çıkar
            self.db.child("rooms").child(self.current_room).child("members").child(self.user_id).remove()
            
            # Üye sayısını güncelle
            current_members = self.db.child("rooms").child(self.current_room).child("members").get().val()
            member_count = len(current_members) if current_members else 0
            self.db.child("rooms").child(self.current_room).update({'member_count': member_count})
            
            print(f"{Fore.YELLOW}👋 Odadan ayrıldınız.{Style.RESET_ALL}")
            
            self.stop_listening()
            self.current_room = None
            self.last_sent_message_time = None  # Son mesaj zamanını sıfırla
            
        except Exception as e:
            print(f"{Fore.RED}❌ Odadan ayrılma hatası: {e}{Style.RESET_ALL}")
    
    def send_message(self, message):
        """Mesaj gönder"""
        if not self.current_room:
            print(f"{Fore.RED}❌ Önce bir odaya katılın!{Style.RESET_ALL}")
            return
        
        try:
            current_time = datetime.datetime.now()
            message_data = {
                'user_id': self.user_id,
                'username': self.username,
                'message': message,
                'timestamp': current_time.isoformat(),
                'type': 'user'
            }
            
            # Son gönderdiğimiz mesajın zamanını kaydet
            self.last_sent_message_time = current_time
            
            # Mesajı Firebase'e gönder
            self.db.child("rooms").child(self.current_room).child("messages").push(message_data)
            
            # Kendi mesajımızı hemen ekranda göster - cursor'ı yukarı taşı
            timestamp_str = current_time.strftime('%H:%M')
            
            # Cursor'ı yukarı taşı, satırı temizle ve mesajı yazdır
            sys.stdout.write('\033[A')  # Cursor'ı bir satır yukarı taşı
            sys.stdout.write('\033[K')  # Satırı temizle
            print(f"{Fore.GREEN}[{timestamp_str}] {self.username} (Sen): {Style.RESET_ALL}{message}")
            sys.stdout.flush()
            
        except Exception as e:
            print(f"{Fore.RED}❌ Mesaj gönderme hatası: {e}{Style.RESET_ALL}")
    
    def send_system_message(self, message):
        """Sistem mesajı gönder"""
        if not self.current_room:
            return
        
        try:
            message_data = {
                'message': message,
                'timestamp': datetime.datetime.now().isoformat(),
                'type': 'system'
            }
            
            self.db.child("rooms").child(self.current_room).child("messages").push(message_data)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Sistem mesajı hatası: {e}{Style.RESET_ALL}")
    
    def show_chat_history(self, limit=20):
        """Sohbet geçmişini göster"""
        if not self.current_room:
            return
        
        try:
            messages = self.db.child("rooms").child(self.current_room).child("messages").get().val()
            
            if not messages:
                print(f"{Fore.YELLOW}📭 Bu odada henüz mesaj yok. İlk mesajı siz yazın!{Style.RESET_ALL}")
                return
            
            print(f"\n{Fore.CYAN}📜 SOHBET GEÇMİŞİ (Son {limit} mesaj):{Style.RESET_ALL}")
            print("=" * 50)
            
            # Mesajları zamana göre sırala ve son N tanesini al
            message_list = []
            for msg_id, msg_data in messages.items():
                message_list.append(msg_data)
            
            # Zamana göre sırala
            message_list.sort(key=lambda x: x['timestamp'])
            
            # Son N mesajı al
            recent_messages = message_list[-limit:] if len(message_list) > limit else message_list
            
            # Mesajları göster
            for msg in recent_messages:
                timestamp = datetime.datetime.fromisoformat(msg['timestamp']).strftime('%d/%m %H:%M')
                
                if msg['type'] == 'system':
                    print(f"{Fore.YELLOW}🔔 [{timestamp}] {msg['message']}{Style.RESET_ALL}")
                else:
                    if msg.get('user_id') == self.user_id:
                        # Kendi mesajlarımız - yeşil renkte
                        print(f"{Fore.GREEN}[{timestamp}] {msg['username']} (Sen): {Style.RESET_ALL}{msg['message']}")
                    else:
                        # Başkalarının mesajları - mavi renkte
                        print(f"{Fore.CYAN}[{timestamp}] {msg['username']}: {Style.RESET_ALL}{msg['message']}")
            
            print("=" * 50)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Sohbet geçmişi alınamadı: {e}{Style.RESET_ALL}")
    
    def start_listening(self):
        """Mesaj dinlemeyi başlat"""
        if self.listening or not self.current_room:
            return
        
        self.listening = True
        self.listener_thread = threading.Thread(target=self._listen_messages)
        self.listener_thread.daemon = True
        self.listener_thread.start()
    
    def stop_listening(self):
        """Mesaj dinlemeyi durdur"""
        self.listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1)
    
    def _listen_messages(self):
        """Mesajları dinle (arka plan thread'i)"""
        # Başlangıç zamanını şu an olarak ayarla (geçmiş mesajları gösterme)
        last_message_time = datetime.datetime.now()
        
        while self.listening:
            try:
                messages = self.db.child("rooms").child(self.current_room).child("messages").get().val()
                
                if messages:
                    # Yeni mesajları filtrele
                    new_messages = []
                    for msg_id, msg_data in messages.items():
                        msg_time = datetime.datetime.fromisoformat(msg_data['timestamp'])
                        if msg_time > last_message_time:
                            # Kendi gönderdiğimiz mesajı atlayalım (zaten gösterildi)
                            if (msg_data.get('user_id') == self.user_id and 
                                self.last_sent_message_time and 
                                abs((msg_time - self.last_sent_message_time).total_seconds()) < 2):
                                continue
                            new_messages.append(msg_data)
                    
                    # Yeni mesajları göster
                    for msg in sorted(new_messages, key=lambda x: x['timestamp']):
                        if msg['type'] == 'system':
                            # Cursor'ı yukarı taşı, satırı temizle ve sistem mesajını yazdır
                            sys.stdout.write('\033[A')  # Cursor'ı bir satır yukarı taşı
                            sys.stdout.write('\033[K')  # Satırı temizle
                            print(f"{Fore.YELLOW}🔔 {msg['message']}{Style.RESET_ALL}")
                            sys.stdout.flush()
                        else:
                            # Tüm kullanıcı mesajlarını göster (kendi mesajlarımız zaten filtrelendi)
                            timestamp = datetime.datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
                            # Cursor'ı yukarı taşı, satırı temizle ve mesajı yazdır
                            sys.stdout.write('\033[A')  # Cursor'ı bir satır yukarı taşı
                            sys.stdout.write('\033[K')  # Satırı temizle
                            print(f"{Fore.CYAN}[{timestamp}] {msg['username']}: {Style.RESET_ALL}{msg['message']}")
                            sys.stdout.flush()
                    
                    if new_messages:
                        last_message_time = datetime.datetime.now()
                
                time.sleep(1)  # 1 saniye bekle
                
            except Exception as e:
                if self.listening:  # Sadece hala dinliyorsak hata göster
                    print(f"{Fore.RED}❌ Mesaj dinleme hatası: {e}{Style.RESET_ALL}")
                time.sleep(2)
    
    def list_rooms(self):
        """Mevcut odaları listele"""
        try:
            rooms = self.db.child("rooms").get().val()
            
            if not rooms:
                print(f"{Fore.YELLOW}📭 Henüz hiç oda oluşturulmamış.{Style.RESET_ALL}")
                return []
            
            print(f"\n{Fore.CYAN}🏠 MEVCUT ODALAR:{Style.RESET_ALL}")
            print("-" * 50)
            
            room_list = []
            for room_id, room_data in rooms.items():
                member_count = room_data.get('member_count', 0)
                created_time = room_data.get('created_at', 'Bilinmiyor')[:16].replace('T', ' ')
                
                print(f"{Fore.GREEN}📋 {room_data['name']}{Style.RESET_ALL}")
                print(f"   🆔 ID: {Fore.YELLOW}{room_id}{Style.RESET_ALL}")
                print(f"   👥 Üyeler: {member_count}")
                print(f"   📅 Oluşturulma: {created_time}")
                print("-" * 30)
                
                room_list.append({
                    'id': room_id,
                    'name': room_data['name'],
                    'member_count': member_count
                })
            
            return room_list
            
        except Exception as e:
            print(f"{Fore.RED}❌ Oda listesi alınamadı: {e}{Style.RESET_ALL}")
            return []
    
    def get_room_members(self):
        """Mevcut odadaki üyeleri listele"""
        if not self.current_room:
            print(f"{Fore.RED}❌ Önce bir odaya katılın!{Style.RESET_ALL}")
            return
        
        try:
            members = self.db.child("rooms").child(self.current_room).child("members").get().val()
            
            if members:
                print(f"\n{Fore.CYAN}👥 ODADA BULUNANLAR:{Style.RESET_ALL}")
                print("-" * 30)
                for user_id, username in members.items():
                    status = "🟢" if user_id == self.user_id else "👤"
                    print(f"{status} {username}")
                print("-" * 30)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Üye listesi alınamadı: {e}{Style.RESET_ALL}")