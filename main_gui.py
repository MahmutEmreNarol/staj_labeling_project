import tkinter as tk
from tkinter import messagebox
from auth import login, register
root = tk.Tk()
root.title("Giriş Ekranı")
root.geometry("350x250")

email_label=tk.Label(root,text="Eposta :")
email_entry=tk.Entry(root)
password_label=tk.Label(root,text="Şifreniz :")
password_entry=tk.Entry(root)
email_label.pack( pady=(20,5))
email_entry.pack()

password_label.pack()
password_entry.pack()

def giris_yap_tiklandi():
    girilen_email = email_entry.get()
    girilen_password=password_entry.get()
    print("Girilen Email:", girilen_email)
    print("Girilen password:",girilen_password)
    sonuc = login(girilen_email, girilen_password)
    print(sonuc)

    if sonuc:
        messagebox.showinfo("Giriş başarılı")
        root.destroy()
    else:
        messagebox.showerror("Giriş başarısız")

login_btn=tk.Button(root,text="Giriş Yap",command=giris_yap_tiklandi)
login_btn.pack()




root.mainloop()

panel =tk.Tk()
panel.title("Ana Panel")
panel.geometry("400x300")

panel_label=tk.Label(panel ,text="Ana Panele Hoşgeldiniz")
panel_label.pack(pady=20)
panel.mainloop()
