import sqlite3

def örnek_kullanici_ekle():
    con = sqlite3.connect("data_labeling.db")
    cur = con.cursor()


    sorgu = "INSERT INTO users (email, password_hash) VALUES (?, ?)"
    

    cur.execute(sorgu, ("admin@staj.com", "123456"))


    con.commit()


    con.close()
    print("Örnek kullanıcı başarıyla eklendi!")


örnek_kullanici_ekle()