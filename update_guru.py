import sqlite3

conn = sqlite3.connect("data.db")
cur = conn.cursor()

cur.execute("ALTER TABLE guru ADD COLUMN mapel_id INTEGER")

conn.commit()
conn.close()

print("Kolom mapel_id berhasil ditambahkan.")
