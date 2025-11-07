import warnings
warnings.filterwarnings("ignore")

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import subprocess
import os
import sys
import time
import socket
import threading
import platform
import urllib.request
import zipfile
import ssl
from pathlib import Path

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(application_path)

try:
    from winotify import Notification, audio
    WINOTIFY_AVAILABLE = True
    TOAST_AVAILABLE = False
except:
    WINOTIFY_AVAILABLE = False
    try:
        from win10toast import ToastNotifier
        TOAST_AVAILABLE = True
    except:
        TOAST_AVAILABLE = False

class SystemVPN:
    def __init__(self):
        self.v2ray_process = None
        self.config_file = "vpn_config.json"
        self.sertifika = "meb.cer"
        self.v2ray_path = None
        self.running = False
        
        self.working_dir = os.getcwd()
        
        if WINOTIFY_AVAILABLE:
            self.notification_type = "winotify"
        elif TOAST_AVAILABLE:
            self.toaster = ToastNotifier()
            self.notification_type = "toast"
        else:
            self.notification_type = "popup"
        
        self.window = tk.Tk()
        self.window.title("Engel Aşıcı VPN")
        self.window.geometry("450x400")
        self.window.resizable(False, False)
        
        self.icon_path = "vpn_icon.ico"
        if os.path.exists(self.icon_path):
            try:
                self.window.iconbitmap(self.icon_path)
            except:
                pass
        
        self.colors = {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'accent': '#89b4fa',
            'success': '#a6e3a1',
            'error': '#f38ba8',
            'warning': '#f9e2af',
            'panel': '#313244',
            'button_success': '#a6e3a1',
            'button_error': '#f38ba8'
        }
        
        self.window.configure(bg=self.colors['bg'])
        
        self.setup_gui()
        
    def setup_gui(self):
        container = tk.Frame(self.window, bg=self.colors['bg'])
        container.pack(expand=True, fill="both", padx=25, pady=25)
        
        header_frame = tk.Frame(container, bg=self.colors['bg'])
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_container = tk.Frame(header_frame, bg=self.colors['bg'])
        title_container.pack()
        
        icon_label = tk.Label(
            title_container,
            text="🛡️",
            font=("Segoe UI Emoji", 32),
            bg=self.colors['bg'],
            fg=self.colors['accent']
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        title = tk.Label(
            title_container,
            text="Engel Aşıcı VPN",
            font=("Segoe UI", 22, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        title.pack(side="left")
        
        self.status_panel = tk.Frame(
            container,
            bg=self.colors['panel'],
            relief="flat",
            bd=0
        )
        self.status_panel.pack(fill="x", pady=15, ipady=10)
        
        self.status_icon = tk.Label(
            self.status_panel,
            text="●",
            font=("Segoe UI", 24),
            bg=self.colors['panel'],
            fg=self.colors['error']
        )
        self.status_icon.pack(pady=5)
        
        self.status_label = tk.Label(
            self.status_panel,
            text="BAĞLI DEĞİL",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['fg']
        )
        self.status_label.pack(pady=5)
        
        self.detail_label = tk.Label(
            self.status_panel,
            text="VPN bağlantısı kapalı",
            font=("Segoe UI", 9),
            bg=self.colors['panel'],
            fg=self.colors['fg'],
            wraplength=350
        )
        self.detail_label.pack(pady=(0, 10))
        
        self.progress = ttk.Progressbar(
            self.status_panel,
            mode='indeterminate',
            length=300
        )
        
        button_frame = tk.Frame(container, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        self.toggle_button = tk.Button(
            button_frame,
            text="▶ BAŞLAT",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['button_success'],
            fg=self.colors['bg'],
            activebackground=self.colors['success'],
            activeforeground=self.colors['bg'],
            width=20,
            height=2,
            border=0,
            cursor="hand2",
            relief="flat",
            command=self.toggle_vpn
        )
        self.toggle_button.pack()
        
        self.toggle_button.bind("<Enter>", self.on_button_hover)
        self.toggle_button.bind("<Leave>", self.on_button_leave)
        
        info_frame = tk.Frame(container, bg=self.colors['bg'])
        info_frame.pack(side="bottom", fill="x", pady=(20, 0))
        
        dir_label = tk.Label(
            info_frame,
            text=f"📁 {os.path.basename(self.working_dir)}",
            font=("Segoe UI", 7),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        dir_label.pack(side="left")
        
        info_label = tk.Label(
            info_frame,
            text="Sistem geneli VPN",
            font=("Segoe UI", 9, "italic"),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        info_label.pack(side="right")
        
    def on_button_hover(self, event):
        if self.running:
            self.toggle_button.config(bg='#e63946')
        else:
            self.toggle_button.config(bg='#94d2bd')
            
    def on_button_leave(self, event):
        if self.running:
            self.toggle_button.config(bg=self.colors['button_error'])
        else:
            self.toggle_button.config(bg=self.colors['button_success'])
        
    def change_icon(self):
        file_path = filedialog.askopenfilename(
            title="İkon Seç",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy(file_path, self.icon_path)
                self.window.iconbitmap(self.icon_path)
                self.show_notification("İkon değiştirildi", "Yeni ikon ayarlandı", success=True)
            except Exception as e:
                messagebox.showerror("Hata", f"İkon ayarlanamadı:\n{e}")
                
    def show_notification(self, title, message, success=True):
        if self.notification_type == "winotify":
            try:
                toast = Notification(
                    app_id="Engel Aşıcı VPN",
                    title=title,
                    msg=message,
                    duration="short"
                )
                
                if os.path.exists(self.icon_path):
                    toast.set_icon(self.icon_path)
                    
                toast.show()
            except:
                self.show_popup_notification(title, message, success)
                
        elif self.notification_type == "toast":
            try:
                icon_path = self.icon_path if os.path.exists(self.icon_path) else None
                self.toaster.show_toast(
                    title,
                    message,
                    duration=3,
                    icon_path=icon_path,
                    threaded=True
                )
            except:
                self.show_popup_notification(title, message, success)
        else:
            self.show_popup_notification(title, message, success)
        
    def show_popup_notification(self, title, message, success=True):
        notif = tk.Toplevel(self.window)
        notif.title("")
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)
        
        screen_width = notif.winfo_screenwidth()
        screen_height = notif.winfo_screenheight()
        notif.geometry(f"300x100+{screen_width-320}+{screen_height-150}")
        
        bg_color = self.colors['success'] if success else self.colors['error']
        notif.configure(bg=bg_color)
        
        frame = tk.Frame(notif, bg=bg_color)
        frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        title_label = tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg=self.colors['bg']
        )
        title_label.pack(anchor="w")
        
        msg_label = tk.Label(
            frame,
            text=message,
            font=("Segoe UI", 9),
            bg=bg_color,
            fg=self.colors['bg'],
            wraplength=270,
            justify="left"
        )
        msg_label.pack(anchor="w", pady=(5, 0))
        
        notif.after(3000, notif.destroy)
        
    def update_status(self, status, detail, icon_color=None):
        self.status_label.config(text=status)
        self.detail_label.config(text=detail)
        
        if icon_color:
            self.status_icon.config(fg=icon_color)
            
    def show_connecting(self):
        self.update_status(
            "BAĞLANIYOR...",
            "VPN sunucusuna bağlanılıyor, lütfen bekleyin",
            self.colors['warning']
        )
        
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        self.toggle_button.config(state="disabled", text="⏳ BAĞLANIYOR...")
        
    def hide_connecting(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.toggle_button.config(state="normal")
        
    def find_or_download_v2ray(self):
        if os.path.exists("v2ray.exe"):
            return "v2ray.exe"
        if os.path.exists("v2ray"):
            return "v2ray"
            
        self.update_status(
            "İNDİRİLİYOR...",
            "V2Ray indiriliyor, bu birkaç dakika sürebilir",
            self.colors['warning']
        )
        
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        sistem = platform.system().lower()
        
        if sistem == "windows":
            exe_name = "v2ray.exe"
            url = "https://github.com/v2fly/v2ray-core/releases/download/v5.1.0/v2ray-windows-64.zip"
        else:
            exe_name = "v2ray"
            url = "https://github.com/v2fly/v2ray-core/releases/download/v5.1.0/v2ray-linux-64.zip"
            
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            
            urllib.request.urlretrieve(url, "v2ray.zip")
            
            self.detail_label.config(text="Dosyalar çıkarılıyor...")
            
            with zipfile.ZipFile("v2ray.zip", 'r') as zip_ref:
                zip_ref.extractall("v2ray_temp")
                
            import shutil
            for root, dirs, files in os.walk("v2ray_temp"):
                for file in files:
                    if file.lower() in ["v2ray.exe", "v2ray", "wv2ray.exe"]:
                        src = os.path.join(root, file)
                        shutil.copy2(src, exe_name)
                        
                        for data_file in ["geoip.dat", "geosite.dat"]:
                            data_src = os.path.join(root, data_file)
                            if os.path.exists(data_src):
                                shutil.copy2(data_src, data_file)
                        break
                        
            os.remove("v2ray.zip")
            if os.path.exists("v2ray_temp"):
                shutil.rmtree("v2ray_temp")
                
            if sistem != "windows":
                os.chmod(exe_name, 0o755)
                
            self.progress.stop()
            self.progress.pack_forget()
            
            return exe_name
            
        except Exception as e:
            self.progress.stop()
            self.progress.pack_forget()
            self.update_status(
                "HATA",
                f"V2Ray indirilemedi: {str(e)}",
                self.colors['error']
            )
            self.show_notification("İndirme Hatası", f"V2Ray indirilemedi:\n{str(e)}", success=False)
            return None
            
    def create_config(self):
        config = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "port": 10808,
                    "listen": "127.0.0.1",
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth",
                        "udp": True
                    }
                },
                {
                    "port": 10809,
                    "listen": "127.0.0.1",
                    "protocol": "http"
                }
            ],
            "outbounds": [
                {
                    "protocol": "vmess",
                    "settings": {
                        "vnext": [
                            {
                                "address": "149.91.1.15",
                                "port": 443,
                                "users": [
                                    {
                                        "id": "6be3e1b2-05e1-46a1-ad36-70aaabaa8d12",
                                        "alterId": 0,
                                        "security": "auto"
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "network": "ws",
                        "security": "tls",
                        "wsSettings": {
                            "path": "/vmess-ws-public",
                            "headers": {
                                "Host": "api.whatsapp.net"
                            }
                        },
                        "tlsSettings": {
                            "serverName": "api.whatsapp.net",
                            "allowInsecure": True,
                            "alpn": ["http/1.1"]
                        },
                        "sockopt": {
                            "tcpFastOpen": True,
                            "tcpNoDelay": True
                        }
                    },
                    "mux": {
                        "enabled": True,
                        "concurrency": 8
                    }
                }
            ]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
    def set_windows_proxy(self, enable=True):
        if platform.system() != "Windows":
            return
            
        try:
            import winreg
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                0, winreg.KEY_ALL_ACCESS
            )
            
            if enable:
                winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, 'ProxyServer', 0, winreg.REG_SZ, '127.0.0.1:10809')
                winreg.SetValueEx(key, 'ProxyOverride', 0, winreg.REG_SZ, 
                    'localhost;127.*;10.*;192.168.*;*.local;<local>')
            else:
                winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 0)
                
            winreg.CloseKey(key)
            
            import ctypes
            internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
            internet_set_option(0, 39, 0, 0)
            internet_set_option(0, 37, 0, 0)
            
        except Exception as e:
            pass
            
    def check_connection(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 10808))
            sock.close()
            return result == 0
        except:
            return False
            
    def start_vpn_thread(self):
        self.window.after(0, self.show_connecting)
        
        if not self.v2ray_path:
            self.v2ray_path = self.find_or_download_v2ray()
            
        if not self.v2ray_path:
            self.window.after(0, self.hide_connecting)
            self.window.after(0, lambda: self.update_status(
                "HATA",
                "V2Ray bulunamadı veya indirilemedi",
                self.colors['error']
            ))
            self.window.after(0, lambda: self.show_notification(
                "Bağlantı Başarısız",
                "V2Ray bulunamadı. Lütfen manuel olarak indirin.",
                success=False
            ))
            return
            
        try:
            self.create_config()
            
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                
                self.v2ray_process = subprocess.Popen(
                    [self.v2ray_path, "run", "-c", self.config_file],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    startupinfo=startupinfo
                )
            else:
                self.v2ray_process = subprocess.Popen(
                    [self.v2ray_path, "run", "-c", self.config_file],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
            connected = False
            for i in range(10):
                time.sleep(0.5)
                if self.check_connection():
                    connected = True
                    break
                    
            if connected:
                self.set_windows_proxy(True)
                self.running = True
                
                self.window.after(0, self.hide_connecting)
                self.window.after(0, lambda: self.update_status(
                    "BAĞLI",
                    "VPN aktif - Tüm internet trafiği güvenli",
                    self.colors['success']
                ))
                self.window.after(0, lambda: self.toggle_button.config(
                    text="■ DURDUR",
                    bg=self.colors['button_error'],
                    activebackground=self.colors['error']
                ))
                
                self.window.after(0, lambda: self.show_notification(
                    "VPN Bağlandı",
                    "Artık tüm engelli sitelere erişebilirsiniz!",
                    success=True
                ))
                
            else:
                raise Exception("Bağlantı zaman aşımına uğradı")
                
        except Exception as e:
            self.stop_vpn()
            
            error_msg = str(e)
            self.window.after(0, self.hide_connecting)
            self.window.after(0, lambda: self.update_status(
                "BAĞLANTI BAŞARISIZ",
                f"Sunucuya bağlanılamadı: {error_msg}",
                self.colors['error']
            ))
            self.window.after(0, lambda: self.show_notification(
                "Bağlantı Başarısız",
                f"VPN sunucusuna bağlanılamadı.\n{error_msg}",
                success=False
            ))
            
    def start_vpn(self):
        thread = threading.Thread(target=self.start_vpn_thread)
        thread.daemon = True
        thread.start()
        
    def stop_vpn(self):
        self.set_windows_proxy(False)
        
        if self.v2ray_process:
            try:
                self.v2ray_process.terminate()
                time.sleep(1)
                if self.v2ray_process.poll() is None:
                    self.v2ray_process.kill()
            except:
                pass
            self.v2ray_process = None
            
        if os.path.exists(self.config_file):
            try:
                os.remove(self.config_file)
            except:
                pass
                
        self.running = False
        
        self.update_status(
            "BAĞLI DEĞİL",
            "VPN bağlantısı kapalı",
            self.colors['error']
        )
        self.toggle_button.config(
            text="▶ BAŞLAT",
            bg=self.colors['button_success'],
            activebackground=self.colors['success']
        )
        
        self.show_notification(
            "VPN Kapatıldı",
            "Normal internet bağlantısına dönüldü",
            success=True
        )
        
    def toggle_vpn(self):
        if self.running:
            self.stop_vpn()
        else:
            self.start_vpn()
            
    def on_closing(self):
        if self.running:
            if messagebox.askokcancel("Çıkış", "VPN çalışıyor. Kapatmak istediğinize emin misiniz?"):
                self.stop_vpn()
                self.window.destroy()
        else:
            self.window.destroy()
            
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.update_status(
            "HAZIR",
            "Aşağıdaki yeşil BAŞLAT butonuna tıklayın",
            self.colors['accent']
        )
        
        self.window.mainloop()

def main():
    print(f"[*] Çalışma dizini: {os.getcwd()}")
    
    if platform.system() == "Windows":
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Yönetici Yetkisi Gerekli",
                "Bu program yönetici olarak çalıştırılmalıdır.\n\n"
                "Sağ tıklayıp 'Yönetici olarak çalıştır' seçin."
            )
            root.destroy()
            sys.exit(1)
            
    app = SystemVPN()
    app.run()

if __name__ == "__main__":
    main()