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

c.execute("""CREATE TABLE penugasan (
    id_penugasan INTEGER PRIMARY KEY AUTOINCREMENT,
    id_hasil INTEGER,
    id_slot INTEGER,
    id_kelas INTEGER,
    id_guru INTEGER,
    id_mapel INTEGER
)""")

c.execute("""CREATE TABLE param_pso (
    id_param INTEGER PRIMARY KEY AUTOINCREMENT,
    populasi INTEGER,
    generasi INTEGER,
    w REAL,
    c1 REAL,
    c2 REAL,
    mut_rate REAL
)""")

c.execute("""CREATE TABLE hasil_pso (
    id_hasil INTEGER PRIMARY KEY AUTOINCREMENT,
    id_param INTEGER,
    tanggal TEXT,
    fitness_terbaik REAL
)""")

c.execute("""CREATE TABLE pelanggaran (
    id_pelanggaran INTEGER PRIMARY KEY AUTOINCREMENT,
    id_hasil INTEGER,
    jenis TEXT,
    bobot INTEGER,
    jumlah INTEGER
)""")

gurus = [
    (1,'Ani Nurianti S.Pd',10),
    (2,'Budi Setiadi M.Pd',8),
    (3,'Citra S.Pd',12),
    (4,'Siti Linda S.Kom',6) 
]

mapels = [
    (1,'Matematika',4),
    (2,'IPA',3),
    (3,'TIK',3)
]

kelasses = [
    (1,'7A'),
    (2,'7B'),
    (3,'8A')
]

c.executemany("INSERT INTO guru VALUES (?,?,?)", gurus)
c.executemany("INSERT INTO mapel VALUES (?,?,?)", mapels)
c.executemany("INSERT INTO kelas VALUES (?,?)", kelasses)

hari = ['Senin','Selasa','Rabu','Kamis','Jumat']
idx = 1
slots = []
for h in hari:
    for j in range(1,7):
        slots.append((idx,h,j))
        idx += 1
c.executemany("INSERT INTO slot_waktu VALUES (?,?,?)", slots)

c.execute("""CREATE TABLE IF NOT EXISTS users (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)""")

try:
    c.execute("INSERT INTO users (username,password) VALUES (?,?)", ('admin','admin123'))
except sqlite3.IntegrityError:
    pass  

conn.commit()
conn.close()
print("Database 'data.db' created successfully.")
