import sqlite3
import pandas as pd
from pathlib import Path

#work_list = Path.cwd() / "downloads" / "works_list.xls"
work_list = Path.cwd().parent / "downloads" / "works_list1.xls"

# Delete all works that not in "Drones" category
df = pd.read_excel(work_list)
df = df[df["Category"] == "Дрони"]
df = df[["Name", "Duration (minutes)"]]

#df.to_excel("works_list_test.xlsx")

# Open database
conn = sqlite3.connect('../works.db', timeout=10)
cursor = conn.cursor()
# Table of works and time
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Works (
    Name TEXT PRIMARY KEY,
    Time INTEGER NOT NULL,
    UNIQUE(Name)
)""")

try:
    for i, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO Works (Name, Time) VALUES (?, ?)
        """,(row['Name'], row['Duration (minutes)']))
except Exception as e:
    print('Error in upload_works_list:\n', e)
finally:
    conn.commit()
    conn.close()