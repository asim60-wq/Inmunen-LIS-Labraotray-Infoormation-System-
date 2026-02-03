# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

# API Uygulamasını Başlat
app = FastAPI()

# Gelen Veri Modeli (Şablon)
class KullaniciVerisi(BaseModel):
    kadi: str
    sifre_hash: str

# --- VERİTABANI İŞLEMLERİ ---
def db_baglan():
    conn = sqlite3.connect("bulut_veritabani.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (kadi TEXT PRIMARY KEY, hash TEXT)")
    conn.commit()
    return conn

# --- API ENDPOINTLERİ (KAPILAR) ---

@app.get("/")
def ana_sayfa():
    return {"mesaj": "BioTool API Sunucusu Çalışıyor! 🚀"}

@app.post("/giris")
def giris_yap(veri: KullaniciVerisi):
    conn = db_baglan()
    cursor = conn.cursor()
    
    # Kullanıcıyı ara
    cursor.execute("SELECT * FROM users WHERE kadi = ? AND hash = ?", (veri.kadi, veri.sifre_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"durum": "basarili", "mesaj": "Giriş Onaylandı"}
    else:
        # 401: Yetkisiz Giriş Hatası
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")

@app.post("/kayit")
def kayit_ol(veri: KullaniciVerisi):
    conn = db_baglan()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (veri.kadi, veri.sifre_hash))
        conn.commit()
        conn.close()
        return {"durum": "basarili", "mesaj": "Kayıt Oluşturuldu"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten var")

# Bu dosyayı çalıştırınca sunucu başlar
if __name__ == "__main__":
    import uvicorn
    # Localhost (Kendi bilgisayarın) üzerinde 8000 portundan yayın yap
    uvicorn.run(app, host="127.0.0.1", port=8000)