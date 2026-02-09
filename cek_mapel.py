import sqlite3, pandas as pd

conn = sqlite3.connect("data.db")
df = pd.read_sql_query("SELECT * FROM mapel", conn)
print(df)
