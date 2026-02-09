import sqlite3

DB = "data.db"

with sqlite3.connect(DB) as conn:
    cur = conn.cursor()
    cur.execute("""
    DELETE FROM guru
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM guru
        GROUP BY nama, mapel
    )
    """)
    conn.commit()
    print