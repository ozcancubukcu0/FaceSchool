import sqlite3

# SQLite veritabanı bağlantısı


def get_db_connection():
    conn = sqlite3.connect('veritabanı.db')
    conn.row_factory = sqlite3.Row
    return conn


def bolum_tablosu():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bolum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bolum_ad TEXT,
            bolum_kod TEXT
        )
    ''')
    conn.commit()
    conn.close()


bolum_tablosu()
