import sqlite3

def init_db():
    # 1. SQL dosyasını güvenle okuyoruz
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # 2. Veritabanına bağlanıp betiği çalıştırıyoruz
    with sqlite3.connect("data_labeling.db") as conn:
        conn.executescript(schema_sql)
        
    print("Database created successfully")

if __name__ == "__main__":
    init_db()
    