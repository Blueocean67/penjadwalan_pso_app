import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

tables = ["guru","mapel","kelas","slot_waktu","penugasan","param_pso","hasil_pso","pelanggaran","users"]
for t in tables:
    c.execute(f"DROP TABLE IF EXISTS {t}")

c.execute("""CREATE TABLE guru (
    id_guru INTEGER PRIMARY KEY,
    nama_guru TEXT,
    max_jam INTEGER
)""")

c.execute("""CREATE TABLE mapel (
    id_mapel INTEGER PRIMARY KEY,
    nama_mapel TEXT,
    jam_per_minggu INTEGER
)""")

c.execute("""CREATE TABLE kelas (
    id_kelas INTEGER PRIMARY KEY,
    nama_kelas TEXT
)""")

c.execute("""CREATE TABLE slot_waktu (
    id_slot INTEGER PRIMARY KEY,
    hari TEXT,
    jam_ke INTEGER
)""")

c.execute("""CREATE TABLE users (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)""")

c.execute("INSERT INTO users (username,password) VALUES (?,?)", ('admin','admin123'))

conn.commit()
conn.close()
print("Database 'data.db' berhasil dibuat dan user admin ditambahkan.")
