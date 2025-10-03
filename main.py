#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from firebase_config import FirebaseConfig
from user_manager import UserManager
from chat_manager import ChatManager
from colorama import Fore, Style, Back, init

# Colorama'yı başlat
init()

class ChatApp:
    def __init__(self):
        self.firebase_config = FirebaseConfig()
        self.user_manager = UserManager()
        self.chat_manager = ChatManager()
        self.current_user_id = None
        self.current_username = None
        self.is_running = True
    
    def clear_screen(self):
        """Konsolu temizle"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """Uygulama başlığını göster"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    🔥 CLİ SOHBET UYGULAMASI 🔥               ║
║              Abdullah Ekşi Tarafından Geliştirildi           ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)
    
    def show_main_menu(self):
        """Ana menüyü göster"""
        menu = f"""
{Fore.YELLOW}🔹 ANA MENÜ 🔹{Style.RESET_ALL}
{Fore.GREEN}1.{Style.RESET_ALL} 📝 Kayıt Ol
{Fore.GREEN}2.{Style.RESET_ALL} 🚪 Giriş Yap
{Fore.GREEN}3.{Style.RESET_ALL} ❓ Yardım
{Fore.GREEN}4.{Style.RESET_ALL} 🚪 Çıkış

{Fore.CYAN}Seçiminiz (1-4): {Style.RESET_ALL}"""
        
        return input(menu).strip()
    
    def show_chat_menu(self):
        """Sohbet menüsünü göster"""
        menu = f"""
{Fore.YELLOW}🔹 SOHBET MENÜSÜ 🔹{Style.RESET_ALL}
{Fore.GREEN}1.{Style.RESET_ALL} 🏠 Oda Oluştur
{Fore.GREEN}2.{Style.RESET_ALL} 🚪 Odaya Katıl
{Fore.GREEN}3.{Style.RESET_ALL} 📋 Odaları Listele
{Fore.GREEN}4.{Style.RESET_ALL} 👥 Online Kullanıcılar
{Fore.GREEN}5.{Style.RESET_ALL} 🚪 Çıkış Yap

{Fore.CYAN}Seçiminiz (1-5): {Style.RESET_ALL}"""
        
        return input(menu).strip()
    
    def register_flow(self):
        """Kayıt olma akışı"""
        print(f"\n{Fore.YELLOW}📝 KULLANICI KAYDI{Style.RESET_ALL}")
        print("-" * 30)
        
        username = input(f"{Fore.CYAN}Kullanıcı Adı: {Style.RESET_ALL}").strip()
        if not username:
            print(f"{Fore.RED}❌ Kullanıcı adı boş olamaz!{Style.RESET_ALL}")
            return
        
        email = input(f"{Fore.CYAN}E-posta: {Style.RESET_ALL}").strip()
        if not email:
            print(f"{Fore.RED}❌ E-posta boş olamaz!{Style.RESET_ALL}")
            return
        
        password = input(f"{Fore.CYAN}Şifre (min 6 karakter): {Style.RESET_ALL}").strip()
        if len(password) < 6:
            print(f"{Fore.RED}❌ Şifre en az 6 karakter olmalı!{Style.RESET_ALL}")
            return
        
        success, user_id = self.user_manager.register_user(username, email, password)
        
        if success:
            print(f"{Fore.GREEN}🎉 Kayıt başarılı! Şimdi giriş yapabilirsiniz.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
    
    def login_flow(self):
        """Giriş yapma akışı"""
        print(f"\n{Fore.YELLOW}🚪 KULLANICI GİRİŞİ{Style.RESET_ALL}")
        print("-" * 30)
        
        email = input(f"{Fore.CYAN}E-posta: {Style.RESET_ALL}").strip()
        if not email:
            print(f"{Fore.RED}❌ E-posta boş olamaz!{Style.RESET_ALL}")
            return False
        
        password = input(f"{Fore.CYAN}Şifre: {Style.RESET_ALL}").strip()
        if not password:
            print(f"{Fore.RED}❌ Şifre boş olamaz!{Style.RESET_ALL}")
            return False
        
        success, user_id, username = self.user_manager.login_user(email, password)
        
        if success:
            self.current_user_id = user_id
            self.current_username = username
            return True
        
        input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
        return False
    
    def create_room_flow(self):
        """Oda oluşturma akışı"""
        print(f"\n{Fore.YELLOW}🏠 YENİ ODA OLUŞTUR{Style.RESET_ALL}")
        print("-" * 30)
        
        room_name = input(f"{Fore.CYAN}Oda Adı: {Style.RESET_ALL}").strip()
        if not room_name:
            print(f"{Fore.RED}❌ Oda adı boş olamaz!{Style.RESET_ALL}")
            return
        
        room_id = self.chat_manager.create_room(room_name, self.current_user_id, self.current_username)
        
        if room_id:
            join_choice = input(f"{Fore.CYAN}Oluşturduğunuz odaya şimdi katılmak ister misiniz? (e/h): {Style.RESET_ALL}").strip().lower()
            if join_choice == 'e':
                self.join_room_flow(room_id)
        
        input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
    
    def join_room_flow(self, room_id=None):
        """Odaya katılma akışı"""
        if not room_id:
            print(f"\n{Fore.YELLOW}🚪 ODAYA KATIL{Style.RESET_ALL}")
            print("-" * 30)
            
            # Mevcut odaları listele
            rooms = self.chat_manager.list_rooms()
            if not rooms:
                input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
                return
            
            room_id = input(f"\n{Fore.CYAN}Katılmak istediğiniz oda ID'si (6 haneli sayı): {Style.RESET_ALL}").strip()
            if not room_id:
                print(f"{Fore.RED}❌ Oda ID'si boş olamaz!{Style.RESET_ALL}")
                return
            
            # ID'nin sayısal olup olmadığını kontrol et
            if not room_id.isdigit() or len(room_id) != 6:
                print(f"{Fore.RED}❌ Geçerli bir 6 haneli oda ID'si girin! (örn: 123456){Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
                return
        
        success = self.chat_manager.join_room(room_id, self.current_user_id, self.current_username)
        
        if success:
            self.chat_loop()
    
    def chat_loop(self):
        """Sohbet döngüsü"""
        self.chat_manager.start_listening()
        
        print(f"\n{Fore.GREEN}💬 SOHBET MODU AKTIF{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Komutlar: /quit (çık), /members (üyeler), /history (geçmiş), /help (yardım){Style.RESET_ALL}")
        print("-" * 50)
        
        while True:
            try:
                message = input().strip()
                
                if not message:
                    continue
                
                if message == "/quit":
                    self.chat_manager.leave_room()
                    break
                elif message == "/members":
                    self.chat_manager.get_room_members()
                elif message == "/history":
                    self.chat_manager.show_chat_history()
                elif message == "/help":
                    print(f"""
{Fore.CYAN}📖 SOHBET KOMUTLARI:{Style.RESET_ALL}
/quit     - Odadan çık
/members  - Odadaki üyeleri göster
/history  - Sohbet geçmişini göster
/help     - Bu yardım menüsünü göster
                    """)
                else:
                    self.chat_manager.send_message(message)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️ Çıkış yapılıyor...{Style.RESET_ALL}")
                self.chat_manager.leave_room()
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Hata: {e}{Style.RESET_ALL}")
    
    def show_online_users(self):
        """Online kullanıcıları göster"""
        print(f"\n{Fore.YELLOW}👥 ONLİNE KULLANICILAR{Style.RESET_ALL}")
        print("-" * 30)
        
        online_users = self.user_manager.get_online_users()
        
        if online_users:
            for user in online_users:
                status = "🟢" if user['id'] == self.current_user_id else "👤"
                print(f"{status} {user['username']}")
        else:
            print(f"{Fore.YELLOW}📭 Şu anda online kullanıcı yok.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
    
    def show_help(self):
        """Yardım menüsünü göster"""
        help_text = f"""
{Fore.CYAN}📖 YARDIM MENÜSÜ{Style.RESET_ALL}
{"-" * 40}



{Fore.YELLOW}📱 KULLANIM:{Style.RESET_ALL}
• Kayıt olun veya giriş yapın
• Oda oluşturun veya mevcut odaya katılın
• Mesajlaşmaya başlayın!

{Fore.YELLOW}🔥 ÖZELLİKLER:{Style.RESET_ALL}
• Gerçek zamanlı mesajlaşma
• Çoklu sohbet odaları
• Online kullanıcı takibi
• Güvenli authentication
• Global erişim

{Fore.GREEN}İyi sohbetler! 🚀{Style.RESET_ALL}
        """
        print(help_text)
        input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
    
    def run(self):
        """Ana uygulama döngüsü"""
        # Firebase yapılandırmasını kontrol et
        if not self.firebase_config.verify_config():
            print(f"\n{Fore.RED}❌ Firebase yapılandırması eksik veya hatalı!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Lütfen .env dosyasını kontrol edin ve gerekli bilgileri girin.{Style.RESET_ALL}")
            return
        
        while self.is_running:
            try:
                self.clear_screen()
                self.print_banner()
                
                if not self.current_user_id:
                    # Kullanıcı giriş yapmamış
                    choice = self.show_main_menu()
                    
                    if choice == '1':
                        self.register_flow()
                    elif choice == '2':
                        if self.login_flow():
                            continue  # Giriş başarılı, chat menüsüne geç
                    elif choice == '3':
                        self.show_help()
                    elif choice == '4':
                        self.is_running = False
                    else:
                        print(f"{Fore.RED}❌ Geçersiz seçim!{Style.RESET_ALL}")
                        input(f"{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
                
                else:
                    # Kullanıcı giriş yapmış
                    print(f"{Fore.GREEN}👋 Hoş geldin, {self.current_username}!{Style.RESET_ALL}")
                    choice = self.show_chat_menu()
                    
                    if choice == '1':
                        self.create_room_flow()
                    elif choice == '2':
                        self.join_room_flow()
                    elif choice == '3':
                        self.chat_manager.list_rooms()
                        input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
                    elif choice == '4':
                        self.show_online_users()
                    elif choice == '5':
                        self.user_manager.logout_user(self.current_user_id)
                        self.current_user_id = None
                        self.current_username = None
                    else:
                        print(f"{Fore.RED}❌ Geçersiz seçim!{Style.RESET_ALL}")
                        input(f"{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
                        
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️ Çıkış yapılıyor...{Style.RESET_ALL}")
                if self.current_user_id:
                    self.user_manager.logout_user(self.current_user_id)
                self.is_running = False
            except Exception as e:
                print(f"{Fore.RED}❌ Beklenmeyen hata: {e}{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")

def main():
    """Ana fonksiyon"""
    try:
        app = ChatApp()
        app.run()
    except Exception as e:
        print(f"❌ Uygulama başlatma hatası: {e}")
    finally:
        print("\n👋 Görüşürüz!")

if __name__ == "__main__":
    main()