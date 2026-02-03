# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import time
import threading
import socket
import datetime
import math
import sqlite3
import hashlib
import csv
import json

# --- KÜTÜPHANE KONTROL VE YÜKLEME ---
def kutuphane_kontrol_ve_yukle():
    gerekli_paketler = {"customtkinter": "customtkinter", "PIL": "Pillow", "packaging": "packaging", "requests": "requests"}
    for import_adi, yukleme_adi in gerekli_paketler.items():
        try:
            __import__(import_adi)
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", yukleme_adi])
            except:
                pass
kutuphane_kontrol_ve_yukle()

import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import requests

# --- YARDIMCI FONKSİYONLAR ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- AYARLAR ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "oturum.json"
LOGO_PNG = resource_path("logo.png")
LOGO_ICO = resource_path("logo.ico")
SECILI_DIL = "TR"

# --- RENKLER ---
RENKLER = {
    "bg_header": ("#1E293B", "#1E293B"),
    "bg_card":   ("#DBDBDB", "#04070b"),
    "neon_blue": ("#00B0FF", "#302b63"),
    "border":    ("#B0BEC5", "#dd1818"),
    "text_main": ("#000000", "#FFFFFF"),
    "text_sub":  ("#546E7A", "#94A3B8"),
    "input_bg":  ("#F5F5F5", "#153860"),
    "input_text":("#000000", "#FFFFFF"),
    "primary":   ("#0288D1", "#153860"),
    "primary_hover": ("#01579B", "#2C4B6F"),
    "accent":    ("#D32F2F", "#EF4444"),
    "accent_hover": ("#B71C1C", "#B91C1C"),
    "success":   ("#388E3C", "#22C55E")
}

GRADIENT_THEMES = {
    "Dark": ("#0f0c29", "#24243e"),
    "Light": ("#6DD5FA", "#FFFFFF")
}

# --- BİYOLOJİK SABİTLER ---
FACTORS_VOL = {"L": 1, "mL": 1e-3, "µL": 1e-6}
FACTORS_CONC = {"M": 1, "mM": 1e-3, "µM": 1e-6}
ENZIMLER = {"EcoRI": "GAATTC", "BamHI": "GGATCC", "HindIII": "AAGCTT", "NotI": "GCGGCCGC", "XhoI": "CTCGAG", "AluI": "AGCT"}
KODON_TABLOSU = {'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M', 'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T', 'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K', 'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R', 'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L', 'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P', 'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q', 'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R', 'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V', 'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A', 'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E', 'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G', 'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S', 'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L', 'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_', 'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W'}
AA_AGIRLIKLARI = {'A': 71.04, 'C': 103.14, 'D': 115.09, 'E': 129.12, 'F': 147.18, 'G': 57.05, 'H': 137.14, 'I': 113.16, 'K': 128.17, 'L': 113.16, 'M': 131.20, 'N': 114.10, 'P': 97.12, 'Q': 128.13, 'R': 156.19, 'S': 87.08, 'T': 101.11, 'V': 99.13, 'W': 186.21, 'Y': 163.18, '_': 0, 'X': 0}

DEFAULT_PROTOCOLS = {
    "Standart PCR": "1. Başlangıç Denatürasyonu: 95°C - 3 dk\n2. Döngü (30-35x):\n   - Denatürasyon: 95°C - 30 sn\n   - Bağlanma: 55-60°C - 30 sn\n   - Uzama: 72°C - 1 dk/kb\n3. Final Uzama: 72°C - 5 dk\n4. Saklama: 4°C - ∞",
    "Agaroz Jel (%1)": "1. 100 mL 1X TAE buffer ölç.\n2. 1g Agaroz ekle.\n3. Mikrodalgada kaynat.\n4. 60°C'ye soğut.\n5. 5 µL EtBr ekle.\n6. Kalıba dök."
}

DIL_SOZLUGU = {
    "TR": {
        "user": "Kullanıcı Adı", "pass": "Şifre", "login": "GİRİŞ YAP", "reg": "Kayıt Ol", "rem": "Beni Hatırla", 
        "main_title": "IMMUNEN Biyoinformatik Çözümleri - Laboratuvar İnformasyon Sistemi", 
        "tab1": "Primer Tasarımı", "tab2": "Protein Analiz", "tab3": "Enzim & Jel", "tab4": "Hizalama", "tab5": "Lab Araçları", "tab6": "NIH / NCBI", "tab7": "Envanter", "tab8": "Protokoller", "tab9": "Not Defteri",
        "ph_dna": "DNA Dizisini Buraya Giriniz...", "btn_calc": "HESAPLA", "btn_save": "Excel'e Kaydet", "res_default": "Sonuçlar burada görünecek...",
        "sub_sol": "Çözelti Hazırlama", "sub_unit": "Birim Dönüştürücü", "sub_pcr": "PCR Mastermix", "sub_rpm": "Santrifüj (RPM/RCF)",
        "sol_solid": "Katıdan Çözelti (MW)", "sol_dil": "Seyreltme",
        "unit_vol": "Hacim (L - µL)", "unit_conc": "Derişim (PPM - PPB)",
        "loading": "Sistem Yükleniyor...", "online": "Çevrimiçi", "offline": "Çevrimdışı",
        "nih_lbl": "Gen Erişim No:", "nih_btn": "VERİ İNDİR", "nih_ok": "İndirildi!", "nih_send": "Analize Gönder ➜", "nih_wait": "Bekleyiniz...", "nih_ph": "Örn: NM_001301717",
        "pcr_samples": "Örnek Sayısı:", "pcr_vol": "Tüp Başı Hacim (µL):", "pcr_dead": "Hata Payı (+N tüp):",
        "rpm_rad": "Rotor Yarıçapı (cm):", "rpm_val": "Hız (RPM):", "rpm_res": "G-Force (RCF):",
        "inv_name": "Malzeme Adı:", "inv_qty": "Miktar / Adet:", "inv_loc": "Lokasyon:", "btn_add": "EKLE", "btn_del": "SİL",
        "prot_title": "Protokol Adı:", "prot_content": "Adımlar / İçerik:", "btn_new": "YENİ / TEMİZLE", "btn_save_prot": "KAYDET / GÜNCELLE",
        "note_lbl": "Deney Notları:", "btn_add_note": "NOTU KAYDET", "btn_del_note": "SEÇİLENİ SİL"
    },
    "EN": {
        "user": "Username", "pass": "Password", "login": "LOGIN", "reg": "Register", "rem": "Remember Me", 
        "main_title": "IMMUNEN Informatic Solutions - Laboratory Informatic System", 
        "tab1": "Primer Design", "tab2": "Protein Analysis", "tab3": "Enzyme & Gel", "tab4": "Alignment", "tab5": "Lab Tools", "tab6": "NIH / NCBI", "tab7": "Inventory", "tab8": "Protocols", "tab9": "Notebook",
        "ph_dna": "Enter DNA Sequence here...", "btn_calc": "CALCULATE", "btn_save": "Save to Excel", "res_default": "Results will appear here...",
        "sub_sol": "Solution Prep", "sub_unit": "Unit Converter", "sub_pcr": "PCR Mastermix", "sub_rpm": "Centrifuge (RPM/RCF)",
        "sol_solid": "Solid to Solution", "sol_dil": "Dilution",
        "unit_vol": "Volume", "unit_conc": "Concentration",
        "loading": "System Loading...", "online": "Online", "offline": "Offline",
        "nih_lbl": "Accession No:", "nih_btn": "FETCH DATA", "nih_ok": "Fetched!", "nih_send": "Send to Analysis ➜", "nih_wait": "Please Wait...", "nih_ph": "Ex: NM_001301717",
        "pcr_samples": "Sample Count:", "pcr_vol": "Vol per Tube (µL):", "pcr_dead": "Dead Volume (+N):",
        "rpm_rad": "Rotor Radius (cm):", "rpm_val": "Speed (RPM):", "rpm_res": "G-Force (RCF):",
        "inv_name": "Item Name:", "inv_qty": "Quantity:", "inv_loc": "Location:", "btn_add": "ADD", "btn_del": "DELETE",
        "prot_title": "Protocol Title:", "prot_content": "Steps / Content:", "btn_new": "NEW / CLEAR", "btn_save_prot": "SAVE / UPDATE",
        "note_lbl": "Experiment Notes:", "btn_add_note": "SAVE NOTE", "btn_del_note": "DELETE SELECTED"
    }
}
def t(key): 
    return DIL_SOZLUGU.get(SECILI_DIL, DIL_SOZLUGU["TR"]).get(key, key)

def get_aspect_ratio_image(path, max_size):
    real_path = resource_path(path)
    if not os.path.exists(real_path): return None
    try:
        pil_img = Image.open(real_path)
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
    except: return None

# --- NCBI CLIENT ---
class NCBIClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    @staticmethod
    def fetch_sequence(accession_id):
        params = {"db": "nuccore", "id": accession_id, "rettype": "fasta", "retmode": "text"}
        try:
            response = requests.get(NCBIClient.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            lines = response.text.splitlines()
            if not lines: return None, "Boş veri"
            header = lines[0]; sequence = "".join(lines[1:])
            return sequence, header
        except Exception as e: return None, str(e)

# --- VERİTABANI İŞLEMLERİ ---
def veritabani_olustur():
    try:
        with sqlite3.connect("kullanicilar.db") as conn: 
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS uyeler (kullanici_adi TEXT PRIMARY KEY, sifre TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS envanter (id INTEGER PRIMARY KEY AUTOINCREMENT, kadi TEXT, urun TEXT, miktar TEXT, lokasyon TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS protokoller (id INTEGER PRIMARY KEY AUTOINCREMENT, kadi TEXT, baslik TEXT, icerik TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS notlar (id INTEGER PRIMARY KEY AUTOINCREMENT, kadi TEXT, tarih TEXT, icerik TEXT)")
            
            cursor.execute("SELECT count(*) FROM protokoller")
            if cursor.fetchone()[0] == 0:
                for baslik, icerik in DEFAULT_PROTOCOLS.items():
                    cursor.execute("INSERT INTO protokoller (kadi, baslik, icerik) VALUES (?, ?, ?)", ("GLOBAL", baslik, icerik))
    except Exception as e:
        print(f"Veritabanı Hatası: {e}")

def sifrele(sifre): return hashlib.sha256(sifre.encode('utf-8')).hexdigest()

def uye_ekle(kadi, sifre):
    try:
        with sqlite3.connect("kullanicilar.db") as conn: 
            conn.execute("INSERT INTO uyeler VALUES (?, ?)", (kadi, sifrele(sifre)))
            return True
    except: return False

def giris_kontrol(kadi, sifre):
    hashli = sifre if len(sifre)==64 else sifrele(sifre)
    try:
        with sqlite3.connect("kullanicilar.db") as conn: 
            res = conn.execute("SELECT * FROM uyeler WHERE kullanici_adi = ? AND sifre = ?", (kadi, hashli)).fetchone()
        return res is not None
    except: return False

def envanter_ekle(kadi, urun, miktar, lokasyon):
    with sqlite3.connect("kullanicilar.db") as conn: conn.execute("INSERT INTO envanter (kadi, urun, miktar, lokasyon) VALUES (?, ?, ?, ?)", (kadi, urun, miktar, lokasyon))
def envanter_getir(kadi):
    with sqlite3.connect("kullanicilar.db") as conn: return conn.execute("SELECT id, urun, miktar, lokasyon FROM envanter WHERE kadi = ? ORDER BY id DESC", (kadi,)).fetchall()
def envanter_sil(item_id):
    with sqlite3.connect("kullanicilar.db") as conn: conn.execute("DELETE FROM envanter WHERE id = ?", (item_id,))

def protokol_kaydet(kadi, baslik, icerik, pid=None):
    with sqlite3.connect("kullanicilar.db") as conn:
        if pid: conn.execute("UPDATE protokoller SET baslik=?, icerik=? WHERE id=?", (baslik, icerik, pid))
        else: conn.execute("INSERT INTO protokoller (kadi, baslik, icerik) VALUES (?, ?, ?)", (kadi, baslik, icerik))
def protokol_getir(kadi):
    with sqlite3.connect("kullanicilar.db") as conn: return conn.execute("SELECT id, baslik, icerik FROM protokoller WHERE kadi = ? OR kadi = 'GLOBAL' ORDER BY id DESC", (kadi,)).fetchall()
def protokol_sil(pid):
    with sqlite3.connect("kullanicilar.db") as conn: conn.execute("DELETE FROM protokoller WHERE id = ?", (pid,))

def not_ekle(kadi, icerik):
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect("kullanicilar.db") as conn: conn.execute("INSERT INTO notlar (kadi, tarih, icerik) VALUES (?, ?, ?)", (kadi, tarih, icerik))
def notlari_getir(kadi):
    with sqlite3.connect("kullanicilar.db") as conn: return conn.execute("SELECT id, tarih, icerik FROM notlar WHERE kadi = ? ORDER BY id DESC", (kadi,)).fetchall()
def not_sil(note_id):
    with sqlite3.connect("kullanicilar.db") as conn: conn.execute("DELETE FROM notlar WHERE id = ?", (note_id,))

def oturumu_kaydet(kadi, sifre):
    try:
        with open(CONFIG_FILE, "w") as f: json.dump({"kadi": kadi, "hash": sifrele(sifre), "lang": SECILI_DIL}, f)
    except: pass
def oturumu_sil():
    if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
def otomatik_giris():
    global SECILI_DIL
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f: d = json.load(f); SECILI_DIL = d.get("lang", "TR")
            if giris_kontrol(d["kadi"], d["hash"]): return d["kadi"]
        except: pass
    return None

# --- BİYOLOJİK HESAPLAMA ---
def protein_cevir(dna):
    p = ""; mw = 0
    for i in range(0, len(dna), 3):
        c = dna[i:i+3]
        if len(c)==3: aa=KODON_TABLOSU.get(c,'X'); p+=aa; mw+=AA_AGIRLIKLARI.get(aa,0)
    return p, (mw+18.02 if mw>0 else 0)

def tm_hesapla(d): return 2*(d.count('A')+d.count('T')) + 4*(d.count('G')+d.count('C'))
def ters_kompleman(d): mp={'A':'T','T':'A','C':'G','G':'C'}; return "".join([mp.get(b,b) for b in d[::-1]])
def enzim_kes(d,e): s=ENZIMLER.get(e); return ([],[]) if not s else (d.split(s), [len(p) for p in d.split(s) if p])

def toggle_theme(app_instance):
    current = ctk.get_appearance_mode()
    new_mode = "Light" if current == "Dark" else "Dark"
    ctk.set_appearance_mode(new_mode)
    if hasattr(app_instance, 'main_frame'):
        app_instance.main_frame.update_gradient_colors()

# --- ARAYÜZ SINIFLARI ---
class GradientFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        if "fg_color" not in kwargs:
            kwargs["fg_color"] = "transparent"
        super().__init__(parent, **kwargs)
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, borderwidth=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._draw_gradient)
        self.canvas.bind("<Configure>", self._draw_gradient)
        self.update_gradient_colors()

    def update_gradient_colors(self):
        mode = ctk.get_appearance_mode()
        self.c1, self.c2 = GRADIENT_THEMES.get(mode, GRADIENT_THEMES["Dark"])
        self._draw_gradient()

    def _draw_gradient(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 2 or height < 2: return
        base = Image.new('RGB', (1, 2))
        try:
            c1_rgb = hex_to_rgb(self.c1)
            c2_rgb = hex_to_rgb(self.c2)
            base.putpixel((0, 0), c1_rgb)
            base.putpixel((0, 1), c2_rgb)
        except Exception: return
        img = base.resize((width, height), Image.Resampling.BICUBIC)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.delete("gradient")
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw", tags="gradient")
        self.canvas.lower()

class DNAAnimasyon(ctk.CTkCanvas):
    def __init__(self, parent, width=300, height=100, **kwargs):
        super().__init__(parent, width=width, height=height, bg="#000001", highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.phase = 0
        self.is_running = True
        self.animate()

    def animate(self):
        if not self.winfo_exists():
            self.is_running = False
            return
        self.delete("all")
        base_pairs = 15; amplitude = 20; frequency = 0.4; speed = 0.15 
        center_y = self.height / 2; start_x = 20; spacing = (self.width - 40) / base_pairs
        
        for i in range(base_pairs):
            x = start_x + i * spacing
            angle = (i * frequency) + self.phase
            y_offset = math.sin(angle) * amplitude
            y1 = center_y + y_offset; y2 = center_y - y_offset
            cos_val = math.cos(angle); radius = 3 + (cos_val * 1.5) 
            color1 = "#00E5FF" if cos_val > 0 else "#00838F"
            color2 = "#2979FF" if cos_val > 0 else "#1565C0"
            self.create_line(x, y1, x, y2, fill="#475569", width=1)
            if cos_val > 0:
                self.create_oval(x-radius, y2-radius, x+radius, y2+radius, fill=color2, outline="")
                self.create_oval(x-radius, y1-radius, x+radius, y1+radius, fill=color1, outline="")
            else:
                self.create_oval(x-radius, y1-radius, x+radius, y1+radius, fill=color1, outline="")
                self.create_oval(x-radius, y2-radius, x+radius, y2+radius, fill=color2, outline="")
        self.phase -= speed
        if self.is_running: self.after(30, self.animate)

class BioToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Laboratory Informatic System")
        self.geometry("1100x900")
        self.configure(fg_color="#203A43")
        
        if os.path.exists(LOGO_ICO): self.iconbitmap(LOGO_ICO)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.kadi = None
        self.main_frame = None
        veritabani_olustur()
        k = otomatik_giris()
        
        if k:
            self.kadi = k
            self.show_splash()
        else:
            self.show_login()

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_frame()
        LoginFrame(self.container, self).pack(fill="both", expand=True)

    def show_splash(self):
        self.clear_frame()
        SplashFrame(self.container, self).pack(fill="both", expand=True)

    def show_main(self):
        self.clear_frame()
        self.update_idletasks() # UI'ın kendine gelmesini bekle
        
        try:
            self.main_frame = MainFrame(self.container, self, self.kadi)
            self.main_frame.pack(fill="both", expand=True)
            # Pencere büyütme işlemini güvenli hale getirdik
            self.after(200, self.safe_maximize) 
        except Exception as e:
            print(f"HATA: {e}")
            messagebox.showerror("Hata", f"Ana ekran yüklenirken hata oluştu:\n{e}")

    def safe_maximize(self):
        try:
            self.state('zoomed')
        except:
            try:
                self.geometry("1200x800")
            except: pass

class LoginFrame(GradientFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.c1, self.c2 = GRADIENT_THEMES["Dark"]
        self._draw_gradient()

        # LOGO
        self.logo_img = get_aspect_ratio_image(LOGO_PNG, (130, 130))
        if self.logo_img:
            ctk.CTkLabel(self, text="", image=self.logo_img)\
                .place(relx=0.5, rely=0.30, anchor="center")
        else:
            ctk.CTkLabel(self, text="🧬", font=("Arial", 60),
                         text_color="white")\
                .place(relx=0.5, rely=0.30, anchor="center")

        # Dil Değiştir
        self.btn_lang = ctk.CTkButton(self, text="TR / EN", width=60, height=25,
                                      fg_color="transparent", border_width=1,
                                      border_color="white", text_color="white",
                                      command=self.dil_degistir)
        self.btn_lang.place(relx=0.95, rely=0.02, anchor="ne")

        # Başlık
        ctk.CTkLabel(self, text="Laboratory Information System",
                     font=("Roboto", 21, "bold"),
                     text_color="white")\
            .place(relx=0.5, rely=0.41, anchor="center")

        # Kullanıcı
        self.user = ctk.CTkEntry(self, placeholder_text=t("user"),
                                 height=50, width=300, corner_radius=10,
                                 border_width=0, fg_color="#334155",
                                 text_color="white")
        self.user.place(relx=0.5, rely=0.52, anchor="center")

        # Şifre
        self.pasw = ctk.CTkEntry(self, placeholder_text=t("pass"), show="*",
                                 height=50, width=300, corner_radius=10,
                                 border_width=0, fg_color="#334155",
                                 text_color="white")
        self.pasw.place(relx=0.5, rely=0.60, anchor="center")

        # Hatırla
        self.var_rem = ctk.BooleanVar()
        ctk.CTkCheckBox(self, text=t("rem"), variable=self.var_rem,
                        text_color="white", fg_color=RENKLER["primary"],
                        hover_color=RENKLER["primary_hover"],
                        checkmark_color="white")\
            .place(relx=0.5, rely=0.68, anchor="center")

        # Giriş
        ctk.CTkButton(self, text=t("login"), width=300, height=50,
                      corner_radius=10, fg_color=RENKLER["primary"],
                      hover_color=RENKLER["primary_hover"],
                      font=("Roboto", 16, "bold"),
                      command=self.giris_yap)\
            .place(relx=0.5, rely=0.78, anchor="center")

        # Kayıt Ol
        ctk.CTkButton(self, text=t("reg"), fg_color="transparent",
                      text_color="#94A3B8", hover_color="#334155",
                      font=("Roboto", 14, "bold"),
                      command=self.kayit_ol)\
            .place(relx=0.5, rely=0.85, anchor="center")

    def giris_yap(self):
        u, p = self.user.get(), self.pasw.get()
        if not u or not p:
            return
        if giris_kontrol(u, p):
            if self.var_rem.get():
                oturumu_kaydet(u, p)
            self.controller.kadi = u
            self.controller.show_splash()
        else:
            messagebox.showerror("Hata", "Hatalı Giriş")

    def kayit_ol(self):
        u, p = self.user.get(), self.pasw.get()
        if not u or not p:
            return
        if uye_ekle(u, p):
            messagebox.showinfo("", "Kayıtlı")
        else:
            messagebox.showerror("", "Alınmış")

    def dil_degistir(self):
        global SECILI_DIL
        SECILI_DIL = "EN" if SECILI_DIL == "TR" else "TR"
        self.controller.show_login()


class SplashFrame(GradientFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.c1, self.c2 = GRADIENT_THEMES["Dark"]
        self._draw_gradient()

        # LOGO
        self.logo_img = get_aspect_ratio_image(LOGO_PNG, (150, 150))
        if self.logo_img:
            ctk.CTkLabel(self, text="", image=self.logo_img)\
                .place(relx=0.5, rely=0.38, anchor="center")
        else:
            ctk.CTkLabel(self, text="🧬", font=("Arial", 100),
                         text_color="white")\
                .place(relx=0.5, rely=0.38, anchor="center")

        # Başlık
        ctk.CTkLabel(self, text="LIS",
                     font=("Roboto", 48, "bold"),
                     text_color="white")\
            .place(relx=0.5, rely=0.53, anchor="center")

        # Alt yazı
        ctk.CTkLabel(self, text="Laboratory Information System beta v1",
                     font=("Roboto", 16),
                     text_color="white")\
            .place(relx=0.5, rely=0.60, anchor="center")

        # Animasyon
        self.dna_anim = DNAAnimasyon(self, width=400, height=60)
        self.dna_anim.place(relx=0.5, rely=0.70, anchor="center")

        # Yükleme yazısı
        self.lbl_loading = ctk.CTkLabel(self, text=t("loading") + " %0",
                                        font=("Roboto", 14),
                                        text_color="#00E5FF")
        self.lbl_loading.place(relx=0.5, rely=0.78, anchor="center")

        # Progress
        self.loading_step = 0
        self.after(30, self.update_progress)

    def update_progress(self):
        try:
            self.loading_step += 0.01
            percent = int(self.loading_step * 100)
            self.lbl_loading.configure(text=f"{t('loading')} %{percent}")

            if self.loading_step < 1.0:
                self.after(30, self.update_progress)
            else:
                self.dna_anim.is_running = False
                self.controller.show_main()

        except Exception as e:
            print("Splash error:", e)


class MainFrame(GradientFrame):
    def __init__(self, parent, controller, kadi):
        super().__init__(parent)
        self.controller = controller
        self.kadi = kadi

        self.header = ctk.CTkFrame(
            self, height=90, corner_radius=20,
            fg_color=RENKLER["bg_header"]
        )
        self.header.pack(fill="x")

        self.logo = get_aspect_ratio_image(LOGO_PNG, (50, 50))
        if self.logo:
            ctk.CTkLabel(
                self.header,
                text="",
                image=self.logo,
                fg_color="transparent"
            ).pack(side="left", padx=(20, 15), pady=10)
        else:
            ctk.CTkLabel(
                self.header,
                text="🧬",
                font=("Arial", 35),
                text_color=RENKLER["text_main"],
                fg_color="transparent"
            ).pack(side="left", padx=(20, 15), pady=10)

        ctk.CTkLabel(
            self.header,
            text=t('main_title'),
            font=("Roboto Medium", 22),
            text_color=RENKLER["text_main"],
            fg_color="transparent"
        ).pack(side="left")

        ctk.CTkButton(
            self.header, text="Çıkış", width=100, height=35,
            fg_color=RENKLER["accent"], text_color="white",
            hover_color=RENKLER["accent_hover"],
            command=self.cikis_yap
        ).pack(side="right", padx=20)

        ctk.CTkButton(
            self.header, text="Mod", width=50, height=35,
            fg_color="transparent", border_width=1,
            border_color=RENKLER["text_main"][0],
            text_color=RENKLER["text_main"],
            command=lambda: toggle_theme(self.controller)
        ).pack(side="right", padx=5)

        self.btn_status = ctk.CTkButton(
            self.header, text="● Net",
            width=80, height=30,
            fg_color="transparent",
            border_width=1, border_color="gray",
            text_color="gray", hover=False
        )
        self.btn_status.pack(side="right", padx=5)

        self.tabview = ctk.CTkTabview(
            self, width=1000, height=600,
            corner_radius=15,
            fg_color="transparent",
            segmented_button_fg_color=RENKLER["bg_header"],
            segmented_button_selected_color=RENKLER["primary"],
            text_color=RENKLER["text_main"]
        )
        self.tabview.pack(pady=20, padx=20, fill="none", expand=True)

        self.t1 = self.tabview.add(t("tab1"))
        self.t2 = self.tabview.add(t("tab2"))
        self.t3 = self.tabview.add(t("tab3"))
        self.t4 = self.tabview.add(t("tab4"))
        self.t5 = self.tabview.add(t("tab5"))
        self.t6 = self.tabview.add(t("tab6"))
        self.t7 = self.tabview.add(t("tab7"))
        self.t8 = self.tabview.add(t("tab8"))
        self.t9 = self.tabview.add(t("tab9"))

        try: self.setup_primer()
        except Exception as e: print(f"Tab1 Err: {e}")

        try: self.setup_protein()
        except: pass

        try: self.setup_enzim()
        except: pass

        try: self.setup_align()
        except: pass

        try: self.setup_solution()
        except: pass

        try: self.setup_ncbi()
        except: pass

        try:
            self.setup_inventory()
        except Exception as e:
            print(f"Inv Err: {e}")

        try: self.setup_protocols()
        except: pass

        try: self.setup_notebook()
        except: pass

        self.start_status_check()

    def cikis_yap(self):
        if messagebox.askyesno("IMMUNEN-LIS", "Çıkış yapılsın mı?"):
            oturumu_sil()
            self.controller.show_login()

    def start_status_check(self):
        threading.Thread(target=self._check_net, daemon=True).start()
        self.after(5000, self.start_status_check)

    def _check_net(self):
        try:
            socket.create_connection(("www.google.com", 80), timeout=2)
            is_online = True
        except:
            is_online = False
        self.after(0, lambda: self._update_status_ui(is_online))

    def _update_status_ui(self, is_online):
        if is_online:
            self.btn_status.configure(
                text=f"● {t('online')}",
                text_color="#4CAF50",
                border_color="#4CAF50"
            )
        else:
            self.btn_status.configure(
                text=f"● {t('offline')}",
                text_color="#D32F2F",
                border_color="#D32F2F"
            )

    # --- TAB FONKSİYONLARI ---
    def setup_primer(self):
        card = ctk.CTkFrame(self.t1, fg_color= RENKLER["bg_card"], corner_radius=20, border_width=2, border_color= "#302b63")
        card.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(card, text="Primer Tasarımı", font=("Roboto", 24, "bold"), text_color=RENKLER["text_main"]).pack(pady=(25,10), anchor="w", padx=30)
        self.txt_dna = ctk.CTkTextbox(card, height=120, border_color=RENKLER["text_sub"], border_width=0, fg_color="#182533", text_color="white", corner_radius=10, font=("Consolas", 14))
        self.txt_dna.pack(fill="x", padx=30, pady=(10, 5))
        self.lbl_res_p = ctk.CTkLabel(card, text=t("res_default"), text_color=RENKLER["neon_blue"], font=("Consolas", 12), justify="left")
        self.lbl_res_p.pack(pady=(5, 20), padx=30, anchor="w")
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=0, padx=30, anchor="w")
        ctk.CTkButton(btn_frame, text=t("btn_calc"), width=160, height=45, fg_color=RENKLER["primary"], hover_color=RENKLER["primary_hover"], font=("Roboto", 14, "bold"), command=self.analiz_primer).pack(side="left", padx=(0,15))
        self.btn_save_p = ctk.CTkButton(btn_frame, text=t("btn_save"), width=160, height=45, fg_color=RENKLER["success"], hover_color="#166534", font=("Roboto", 14, "bold"), state="disabled", command=lambda: self.ex_save("primer"))
        self.btn_save_p.pack(side="left")
        self.mem = {}

    def analiz_primer(self):
        dna = self.txt_dna.get("0.0", "end").strip().upper().replace("\n","").replace("ATGC...","")
        if len(dna)<20: return
        f, r = dna[:20], ters_kompleman(dna[-20:]); t1, t2 = tm_hesapla(f), tm_hesapla(r)
        self.lbl_res_p.configure(text=f"Fwd: {f} | Tm: {t1}°C\nRev: {r} | Tm: {t2}°C"); self.mem["primer"] = [f, r, t1, t2]; self.btn_save_p.configure(state="normal")
    
    def ex_save(self, typ):
        f = filedialog.asksaveasfilename(defaultextension=".csv"); 
        if f: 
            with open(f, "w", newline="", encoding="utf-8-sig") as d: csv.writer(d, delimiter=";").writerow(["Fwd",self.mem["primer"][0],self.mem["primer"][2]]); messagebox.showinfo("", "Kaydedildi.")
    
    def setup_protein(self):
        card = ctk.CTkFrame(self.t2, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); card.pack(fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(card, text="Protein Analizi", font=("Roboto Medium", 20), text_color=RENKLER["text_main"]).pack(pady=(20,5), anchor="w", padx=30)
        self.txt_prot_in = ctk.CTkTextbox(card, height=80, border_color=RENKLER["text_sub"], border_width=1, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.txt_prot_in.pack(fill="x", padx=30)
        self.lbl_mw = ctk.CTkLabel(card, text="MW: 0 kDa", text_color=RENKLER["text_sub"]); self.lbl_mw.pack(pady=5)
        self.txt_res_prot = ctk.CTkTextbox(card, height=80, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.txt_res_prot.pack(fill="x", padx=30)
        ctk.CTkButton(card, text="ÇEVİR", fg_color=RENKLER["primary"], width=140, height=40, command=self.run_prot).pack(pady=20, anchor="w", padx=30)
    
    def run_prot(self): 
        d = self.txt_prot_in.get("0.0", "end").strip().upper(); 
        p, w = protein_cevir(d); 
        self.txt_res_prot.delete("0.0", "end"); self.txt_res_prot.insert("0.0", p); 
        self.lbl_mw.configure(text=f"MW: {w/1000:.2f} kDa")
    
    def setup_enzim(self):
        card = ctk.CTkFrame(self.t3, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); card.pack(fill="both", expand=True, padx=5, pady=5); card.columnconfigure(0, weight=1); card.columnconfigure(1, weight=2)
        f_left = ctk.CTkFrame(card, fg_color="transparent"); f_left.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        ctk.CTkLabel(f_left, text="Enzim Kesimi", font=("Roboto Medium", 18), text_color=RENKLER["text_main"]).pack(anchor="w")
        self.txt_enz = ctk.CTkTextbox(f_left, height=150, border_width=1, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.txt_enz.pack(pady=10, fill="x")
        self.cmb_enz = ctk.CTkComboBox(f_left, values=list(ENZIMLER.keys())); self.cmb_enz.pack(pady=5, fill="x")
        ctk.CTkButton(f_left, text="JEL YÜRÜT", fg_color=RENKLER["accent"], command=self.run_gel).pack(pady=20, fill="x")
        self.cvs = ctk.CTkCanvas(card, bg="#212121", highlightthickness=0); self.cvs.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
    def run_gel(self):
        self.cvs.delete("all"); d = self.txt_enz.get("0.0", "end").strip().upper(); _, l = enzim_kes(d, self.cmb_enz.get())
        for i, b in enumerate([1000, 800, 500, 200, 100]): y = 50 + i * 50; self.cvs.create_rectangle(30, y, 70, y+3, fill="gray"); self.cvs.create_text(15, y, text=str(b), fill="white", font=("Arial",8))
        for b in l: 
            y = 300 - (b/4); 
            if y<50: y=50
            self.cvs.create_rectangle(120, y, 180, y+3, fill="#00E5FF", outline="white"); self.cvs.create_text(200, y, text=f"{b}bp", fill="#00E5FF")
    
    def setup_align(self):
        card = ctk.CTkFrame(self.t4, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); card.pack(fill="both", expand=True, padx=5, pady=5)
        self.t_s1 = ctk.CTkEntry(card, placeholder_text="Dizi 1", height=40, text_color=RENKLER["input_text"], fg_color=RENKLER["input_bg"]); self.t_s1.pack(pady=10, padx=30, fill="x")
        self.t_s2 = ctk.CTkEntry(card, placeholder_text="Dizi 2", height=40, text_color=RENKLER["input_text"], fg_color=RENKLER["input_bg"]); self.t_s2.pack(pady=10, padx=30, fill="x")
        self.l_sim = ctk.CTkLabel(card, text="Benzerlik: %0", text_color=RENKLER["primary"], font=("Roboto", 16)); self.l_sim.pack()
        self.cvs_al = ctk.CTkCanvas(card, bg="#212121", height=300); self.cvs_al.pack(fill="x", padx=30, pady=10)
        ctk.CTkButton(card, text="KARŞILAŞTIR", fg_color=RENKLER["primary"], command=self.run_align).pack(pady=10)
    
    def run_align(self):
        self.cvs_al.delete("all"); s1 = self.t_s1.get().upper(); s2 = self.t_s2.get().upper()
        if not s1 or not s2: return
        m = sum(1 for a,b in zip(s1,s2) if a==b); self.l_sim.configure(text=f"Benzerlik: %{(m/max(len(s1),len(s2)))*100:.1f}")
        w = self.cvs_al.winfo_width(); sx = w/len(s1)
        for i,(a,b) in enumerate(zip(s1,s2)):
            if a==b: self.cvs_al.create_line(i*sx, 50, (i+1)*sx, 250, fill="#00FF00", width=2)
    
    def setup_solution(self):
        self.seg_sol = ctk.CTkSegmentedButton(self.t5, values=[t("sub_sol"), t("sub_unit"), t("sub_pcr"), t("sub_rpm")], command=self.sol_switch, selected_color=RENKLER["primary"], unselected_color=RENKLER["input_bg"], text_color=RENKLER["text_main"], height=40); self.seg_sol.pack(pady=10); self.seg_sol.set(t("sub_sol"))
        self.f_p1 = ctk.CTkFrame(self.t5, fg_color="transparent"); self.setup_sol_calc(self.f_p1)
        self.f_p2 = ctk.CTkFrame(self.t5, fg_color="transparent"); self.setup_unit_conv(self.f_p2)
        self.f_p3 = ctk.CTkFrame(self.t5, fg_color="transparent"); self.setup_pcr(self.f_p3)
        self.f_p4 = ctk.CTkFrame(self.t5, fg_color="transparent"); self.setup_rpm(self.f_p4)
        self.f_p1.pack(fill="both", expand=True)
    
    def sol_switch(self, value):
        for f in [self.f_p1, self.f_p2, self.f_p3, self.f_p4]: f.pack_forget()
        if value == t("sub_sol"): self.f_p1.pack(fill="both", expand=True)
        elif value == t("sub_unit"): self.f_p2.pack(fill="both", expand=True)
        elif value == t("sub_pcr"): self.f_p3.pack(fill="both", expand=True)
        elif value == t("sub_rpm"): self.f_p4.pack(fill="both", expand=True)
    
    def calculate_res1(self):
        try:
            self.l_res1.configure(text=f"{float(self.e_mw.get())*float(self.e_conc.get())*1e-3*float(self.e_vol.get())*1e-3:.4f} g")
        except:
            pass

    def calculate_ures(self):
        try:
            self.l_ures.configure(text=f"{(float(self.u_val.get())*FACTORS_VOL[self.cb_u1.get()])/FACTORS_VOL[self.cb_u2.get()]:.4g}")
        except:
            pass

    def setup_sol_calc(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent"); grid.pack(fill="both", expand=True, padx=5, pady=5); grid.columnconfigure(0, weight=1); grid.columnconfigure(1, weight=1)
        c1 = ctk.CTkFrame(grid, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); c1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(c1, text=t("sol_solid"), font=("Roboto Medium", 16), text_color=RENKLER["text_main"]).pack(pady=15)
        self.e_mw = ctk.CTkEntry(c1, placeholder_text="MW", fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.e_mw.pack(pady=5)
        self.e_conc = ctk.CTkEntry(c1, placeholder_text="mM", fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.e_conc.pack(pady=5)
        self.e_vol = ctk.CTkEntry(c1, placeholder_text="mL", fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.e_vol.pack(pady=5)
        self.l_res1 = ctk.CTkLabel(c1, text="...", text_color=RENKLER["primary"], font=("Roboto", 14, "bold")); self.l_res1.pack(pady=10)
        ctk.CTkButton(c1, text="HESAPLA", fg_color=RENKLER["primary"], command=self.calculate_res1).pack(pady=10)
        
        c2 = ctk.CTkFrame(grid, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); c2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(c2, text=t("sol_dil"), font=("Roboto Medium", 16), text_color=RENKLER["text_main"]).pack(pady=15)
        self.e_c1 = ctk.CTkEntry(c2, placeholder_text="C1", fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.e_c1.pack(pady=5)
        self.e_c2 = ctk.CTkEntry(c2, placeholder_text="C2", fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.e_c2.pack(pady=5)
        self.e_v2 = ctk.CTkEntry(c2, placeholder_text="V2", fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.e_v2.pack(pady=5)
        self.l_res2 = ctk.CTkLabel(c2, text="...", text_color=RENKLER["primary"], font=("Roboto", 14, "bold")); self.l_res2.pack(pady=10)
        def run_dil(): 
            try:
                v1=(float(self.e_c2.get())*float(self.e_v2.get()))/float(self.e_c1.get()); self.l_res2.configure(text=f"V1: {v1:.2f} | Su: {float(self.e_v2.get())-v1:.2f}")
            except: pass
        ctk.CTkButton(c2, text="HESAPLA", fg_color=RENKLER["primary"], command=run_dil).pack(pady=10)
    
    def setup_unit_conv(self, parent):
        c = ctk.CTkFrame(parent, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); c.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(c, text=t("sub_unit"), font=("Roboto Medium", 20), text_color=RENKLER["text_main"]).pack(pady=20)
        self.u_val = ctk.CTkEntry(c, placeholder_text="Değer", fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.u_val.pack(pady=10)
        f = ctk.CTkFrame(c, fg_color="transparent"); f.pack(pady=5)
        self.cb_u1 = ctk.CTkComboBox(f, values=list(FACTORS_VOL.keys())); self.cb_u1.pack(side="left", padx=10)
        ctk.CTkLabel(f, text="➜", text_color=RENKLER["text_main"]).pack(side="left")
        self.cb_u2 = ctk.CTkComboBox(f, values=list(FACTORS_VOL.keys())); self.cb_u2.pack(side="left", padx=10)
        self.l_ures = ctk.CTkLabel(c, text="...", text_color=RENKLER["success"], font=("Roboto", 16)); self.l_ures.pack(pady=20)
        ctk.CTkButton(c, text="ÇEVİR", fg_color=RENKLER["success"], command=self.calculate_ures).pack()
    
    def setup_pcr(self, parent):
        c = ctk.CTkFrame(parent, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); c.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(c, text=t("sub_pcr"), font=("Roboto Medium", 20), text_color=RENKLER["text_main"]).pack(pady=20)
        f_in = ctk.CTkFrame(c, fg_color="transparent"); f_in.pack(pady=10)
        ctk.CTkLabel(f_in, text=t("pcr_samples"), text_color=RENKLER["text_main"]).grid(row=0, column=0, padx=10, pady=5); self.e_samp = ctk.CTkEntry(f_in, width=80); self.e_samp.grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(f_in, text=t("pcr_vol"), text_color=RENKLER["text_main"]).grid(row=1, column=0, padx=10, pady=5); self.e_pvol = ctk.CTkEntry(f_in, width=80); self.e_pvol.insert(0,"25"); self.e_pvol.grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkLabel(f_in, text=t("pcr_dead"), text_color=RENKLER["text_main"]).grid(row=2, column=0, padx=10, pady=5); self.e_dead = ctk.CTkEntry(f_in, width=80); self.e_dead.insert(0,"1"); self.e_dead.grid(row=2, column=1, padx=10, pady=5)
        self.txt_pcr = ctk.CTkTextbox(c, height=200, width=400, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.txt_pcr.pack(pady=20)
        def calc_pcr():
            try:
                n = int(self.e_samp.get()) + float(self.e_dead.get()); v = float(self.e_pvol.get())
                mix = {"Buffer (10X)": v*0.1, "dNTPs": v*0.02, "Fwd Primer": v*0.04, "Rev Primer": v*0.04, "Taq": v*0.01, "Template": v*0.08, "Water": 0}
                mix["Water"] = v - sum(mix.values()) + mix["Template"]
                res = f"Total {n} tubes:\n" + "\n".join([f"{k}: {val*n:.1f} µL" for k, val in mix.items() if k!="Template"])
                self.txt_pcr.delete("0.0", "end"); self.txt_pcr.insert("0.0", res)
            except: pass
        ctk.CTkButton(c, text=t("btn_calc"), fg_color=RENKLER["primary"], command=calc_pcr).pack()
    
    def setup_rpm(self, parent):
        c = ctk.CTkFrame(parent, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); c.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(c, text=t("sub_rpm"), font=("Roboto Medium", 20), text_color=RENKLER["text_main"]).pack(pady=20)
        ctk.CTkLabel(c, text=t("rpm_rad"), text_color=RENKLER["text_main"]).pack(pady=5); self.e_rad = ctk.CTkEntry(c); self.e_rad.pack(pady=5)
        ctk.CTkLabel(c, text=t("rpm_val"), text_color=RENKLER["text_main"]).pack(pady=5); self.e_rpm = ctk.CTkEntry(c); self.e_rpm.pack(pady=5)
        self.l_rcf = ctk.CTkLabel(c, text="...", text_color=RENKLER["primary"], font=("Roboto", 24, "bold")); self.l_rcf.pack(pady=20)
        def calc_rcf(): 
            try: r=float(self.e_rad.get()); rpm=float(self.e_rpm.get()); self.l_rcf.configure(text=f"{1.118*1e-5*r*(rpm**2):.0f} x g")
            except: pass
        ctk.CTkButton(c, text=t("btn_calc"), fg_color=RENKLER["primary"], command=calc_rcf).pack()
    
    def setup_ncbi(self):
        card = ctk.CTkFrame(self.t6, fg_color=RENKLER["bg_card"], corner_radius=15, border_width=2, border_color="#302b63"); card.pack(fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(card, text="NCBI GenBank (NIH) Veri Çekme", font=("Roboto Medium", 20), text_color=RENKLER["text_main"]).pack(pady=20)
        ctk.CTkLabel(card, text=t("nih_lbl"), text_color=RENKLER["text_sub"]).pack(pady=5)
        self.e_acc = ctk.CTkEntry(card, placeholder_text=t("nih_ph"), width=300, height=40, text_color=RENKLER["input_text"], fg_color=RENKLER["input_bg"]); self.e_acc.pack(pady=5)
        self.lbl_nih_stat = ctk.CTkLabel(card, text="", text_color=RENKLER["primary"]); self.lbl_nih_stat.pack(pady=10)
        ctk.CTkButton(card, text=t("nih_btn"), width=200, height=45, fg_color="#00695C", hover_color="#004D40", command=self.run_fetch).pack(pady=10)
        self.txt_nih_res = ctk.CTkTextbox(card, height=150, border_color=RENKLER["text_sub"], border_width=1, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.txt_nih_res.pack(fill="x", padx=30, pady=10)
        self.btn_send = ctk.CTkButton(card, text=t("nih_send"), fg_color="#F57F17", state="disabled", command=self.send_to_analysis); self.btn_send.pack(pady=10)
    
    def run_fetch(self):
        acc = self.e_acc.get().strip(); 
        if not acc: return
        self.lbl_nih_stat.configure(text=t("nih_wait")); self.update_idletasks()
        def thread_task():
            seq, header = NCBIClient.fetch_sequence(acc)
            if seq: self.txt_nih_res.delete("0.0", "end"); self.txt_nih_res.insert("0.0", f"Başlık: {header}\n\n{seq}"); self.fetched_seq = seq; self.btn_send.configure(state="normal"); self.lbl_nih_stat.configure(text=t("nih_ok"))
            else: self.lbl_nih_stat.configure(text=f"Hata: {header}")
        threading.Thread(target=thread_task).start()
    
    def send_to_analysis(self):
        self.txt_dna.delete("0.0", "end"); self.txt_dna.insert("0.0", self.fetched_seq); self.tabview.set(t("tab1")); messagebox.showinfo("Bilgi", "Veri aktarıldı.")

    def setup_inventory(self):
        paned = ctk.CTkFrame(self.t7, fg_color="transparent"); paned.pack(fill="both", expand=True, padx=5, pady=5)
        paned.columnconfigure(0, weight=1); paned.columnconfigure(1, weight=2)
        f_add = ctk.CTkFrame(paned, fg_color=RENKLER["bg_card"], border_width=2, border_color="#302b63"); f_add.grid(row=0, column=0, sticky="nsew", padx=5)
        ctk.CTkLabel(f_add, text=t("inv_name"), text_color=RENKLER["text_main"]).pack(pady=5); self.inv_name = ctk.CTkEntry(f_add, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.inv_name.pack(pady=5)
        ctk.CTkLabel(f_add, text=t("inv_qty"), text_color=RENKLER["text_main"]).pack(pady=5); self.inv_qty = ctk.CTkEntry(f_add, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.inv_qty.pack(pady=5)
        ctk.CTkLabel(f_add, text=t("inv_loc"), text_color=RENKLER["text_main"]).pack(pady=5); self.inv_loc = ctk.CTkEntry(f_add, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.inv_loc.pack(pady=5)
        ctk.CTkButton(f_add, text=t("btn_add"), fg_color=RENKLER["success"], command=self.add_inv_item).pack(pady=20)
        self.inv_list_frame = ctk.CTkScrollableFrame(paned, fg_color=RENKLER["bg_card"], border_width=2, border_color="#302b63"); self.inv_list_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        self.refresh_inv()
    def add_inv_item(self):
        n, q, l = self.inv_name.get(), self.inv_qty.get(), self.inv_loc.get()
        if n and q: envanter_ekle(self.kadi, n, q, l); self.refresh_inv(); self.inv_name.delete(0, 'end'); self.inv_qty.delete(0, 'end')
    def refresh_inv(self):
        for w in self.inv_list_frame.winfo_children(): w.destroy()
        for i_id, urun, miktar, lok in envanter_getir(self.kadi):
            row = ctk.CTkFrame(self.inv_list_frame, fg_color=RENKLER["input_bg"]); row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{urun} ({miktar}) - {lok}", text_color=RENKLER["input_text"], anchor="w").pack(side="left", padx=10)
            ctk.CTkButton(row, text="X", width=30, fg_color=RENKLER["accent"], command=lambda x=i_id: self.del_inv(x)).pack(side="right", padx=5)
    def del_inv(self, i_id): envanter_sil(i_id); self.refresh_inv()

    def setup_protocols(self):
        paned = ctk.CTkFrame(self.t8, fg_color="transparent"); paned.pack(fill="both", expand=True, padx=5, pady=5)
        paned.columnconfigure(0, weight=1); paned.columnconfigure(1, weight=2)
        f_list = ctk.CTkScrollableFrame(paned, fg_color=RENKLER["bg_card"], border_width=2, border_color="#302b63"); f_list.grid(row=0, column=0, sticky="nsew", padx=5)
        self.prot_list_frame = f_list
        f_edit = ctk.CTkFrame(paned, fg_color=RENKLER["bg_card"], border_width=2, border_color="#302b63"); f_edit.grid(row=0, column=1, sticky="nsew", padx=5)
        ctk.CTkLabel(f_edit, text=t("prot_title"), text_color=RENKLER["text_main"]).pack(pady=5)
        self.e_prot_title = ctk.CTkEntry(f_edit, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.e_prot_title.pack(fill="x", padx=10)
        ctk.CTkLabel(f_edit, text=t("prot_content"), text_color=RENKLER["text_main"]).pack(pady=5)
        self.txt_prot_content = ctk.CTkTextbox(f_edit, height=300, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.txt_prot_content.pack(fill="both", expand=True, padx=10)
        f_btns = ctk.CTkFrame(f_edit, fg_color="transparent"); f_btns.pack(pady=10)
        ctk.CTkButton(f_btns, text=t("btn_new"), fg_color=RENKLER["primary"], command=self.new_prot).pack(side="left", padx=5)
        ctk.CTkButton(f_btns, text=t("btn_save_prot"), fg_color=RENKLER["success"], command=self.save_prot).pack(side="left", padx=5)
        self.btn_del_prot = ctk.CTkButton(f_btns, text=t("btn_del"), fg_color=RENKLER["accent"], state="disabled", command=self.del_prot); self.btn_del_prot.pack(side="left", padx=5)
        self.current_prot_id = None; self.refresh_protocols()
    def refresh_protocols(self):
        for w in self.prot_list_frame.winfo_children(): w.destroy()
        prots = protokol_getir(self.kadi)
        for pid, baslik, icerik in prots:
            ctk.CTkButton(self.prot_list_frame, text=baslik, fg_color="transparent", border_width=1, border_color="#302b63", text_color=RENKLER["text_main"], command=lambda i=pid, b=baslik, c=icerik: self.load_prot(i, b, c)).pack(fill="x", pady=2)
    def load_prot(self, pid, baslik, icerik):
        self.current_prot_id = pid; self.e_prot_title.delete(0, 'end'); self.e_prot_title.insert(0, baslik)
        self.txt_prot_content.delete("0.0", "end"); self.txt_prot_content.insert("0.0", icerik); self.btn_del_prot.configure(state="normal")
    def new_prot(self): self.current_prot_id = None; self.e_prot_title.delete(0, 'end'); self.txt_prot_content.delete("0.0", "end"); self.btn_del_prot.configure(state="disabled")
    def save_prot(self):
        b = self.e_prot_title.get(); c = self.txt_prot_content.get("0.0", "end").strip()
        if b and c: protokol_kaydet(self.kadi, b, c, self.current_prot_id); self.refresh_protocols(); messagebox.showinfo("", "Kaydedildi.")
    def del_prot(self):
        if self.current_prot_id: protokol_sil(self.current_prot_id); self.new_prot(); self.refresh_protocols()

    def setup_notebook(self):
        paned = ctk.CTkFrame(self.t9, fg_color="transparent"); paned.pack(fill="both", expand=True, padx=5, pady=5)
        paned.columnconfigure(0, weight=1); paned.columnconfigure(1, weight=3)
        f_list = ctk.CTkFrame(paned, fg_color=RENKLER["bg_card"], border_width=2, border_color="#302b63"); f_list.grid(row=0, column=0, sticky="nsew", padx=5)
        ctk.CTkLabel(f_list, text=t("note_lbl"), text_color=RENKLER["text_main"]).pack(pady=10)
        self.list_notes = ctk.CTkScrollableFrame(f_list, fg_color="transparent"); self.list_notes.pack(fill="both", expand=True)
        ctk.CTkButton(f_list, text=t("btn_del_note"), fg_color=RENKLER["accent"], hover_color=RENKLER["accent_hover"], command=self.del_note).pack(pady=10)
        f_write = ctk.CTkFrame(paned, fg_color=RENKLER["bg_card"], border_width=2, border_color="#302b63"); f_write.grid(row=0, column=1, sticky="nsew", padx=5)
        self.txt_note = ctk.CTkTextbox(f_write, height=400, fg_color=RENKLER["input_bg"], text_color=RENKLER["input_text"]); self.txt_note.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkButton(f_write, text=t("btn_add_note"), fg_color=RENKLER["success"], command=self.save_note).pack(pady=10)
        self.refresh_notes()
    def refresh_notes(self):
        for w in self.list_notes.winfo_children(): w.destroy()
        notes = notlari_getir(self.kadi)
        self.note_vars = []
        for n_id, tarih, icerik in notes:
            f = ctk.CTkFrame(self.list_notes, fg_color=RENKLER["input_bg"]); f.pack(fill="x", pady=2)
            var = ctk.IntVar(); self.note_vars.append((n_id, var))
            ctk.CTkCheckBox(f, text=f"{tarih}", variable=var, text_color=RENKLER["input_text"]).pack(side="left", padx=5)
            ctk.CTkButton(f, text=">", width=30, height=20, command=lambda c=icerik: self.show_note(c)).pack(side="right", padx=5)
    def show_note(self, content): self.txt_note.delete("0.0", "end"); self.txt_note.insert("0.0", content)
    def save_note(self):
        content = self.txt_note.get("0.0", "end").strip()
        if content: not_ekle(self.kadi, content); self.refresh_notes(); self.txt_note.delete("0.0", "end")
    def del_note(self):
        for n_id, var in self.note_vars:
            if var.get() == 1: not_sil(n_id)
        self.refresh_notes()

if __name__ == "__main__":
    app = BioToolApp()
    app.mainloop();