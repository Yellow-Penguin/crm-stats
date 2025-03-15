import sqlite3

conn = sqlite3.connect('../works.db', timeout=10)
cursor = conn.cursor()

cursor.execute("""DELETE FROM Reports""")
conn.commit()
conn.close()