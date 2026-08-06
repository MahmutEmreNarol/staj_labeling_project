import sqlite3

def örnek_kullanici_ekle():
    con = sqlite3.connect("data_labeling.db")
    cur = con.cursor()

    # 1. SQL sorgumuzu hazırlıyoruz
    sorgu = "INSERT INTO users (email, password_hash) VALUES (?, ?)"
    
    # 2. Parametreleri güvenli şekilde gönderiyoruz
    cur.execute(sorgu, ("admin@staj.com", "123456"))

    # 3. KRİTİK ADIM: Değişikliği veritabanı dosyasına KAYDEDİYORUZ!
    con.commit()

    # 4. Bağlantıyı kapatıyoruz
    con.close()
    print("Örnek kullanıcı başarıyla eklendi!")


örnek_kullanici_ekle()