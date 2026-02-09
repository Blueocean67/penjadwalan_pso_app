import sqlite3
import pandas as pd

conn = sqlite3.connect("data.db")
df = pd.read_sql_query("PRAGMA table_info(guru)", conn)
conn.close()

print(df)
