# Kendi yazdığımız auth.py modülünden fonksiyonları içeri aktarıyoruz
from auth import register, login, user_exist

print("--- AUTH MODÜLÜ TESTİ ---")

# 1. Yanlış bilgilerle giriş testi
sonuc1 = login("yanlis@mail.com", "000000")
print("Yanlış Giriş Denemesi:", sonuc1)

# 2. Yeni kullanıcı kaydı testi (auth.py içindeki register çalışacak)
kayit_sonucu = register("yeni_kullanici@mail.com", "sifre123")
print("Yeni Kayıt Denemesi:", kayit_sonucu)

# 3. Yeni kaydolunan kullanıcıyla giriş testi (auth.py içindeki login çalışacak)
sonuc2 = login("yeni_kullanici@mail.com", "sifre123")
print("Yeni Kullanıcı Giriş Denemesi:", sonuc2)