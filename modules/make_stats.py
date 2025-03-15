import sqlite3

# TODO: fix PATH`s, add comments, automatically change date

conn = sqlite3.connect('../works.db', timeout=10)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Stats (
        Engineer TEXT PRIMARY KEY,
        TotalTime INTEGER NOT NULL
    )
""")

cursor.execute("""DELETE FROM Stats""")

cursor.execute("""
    INSERT INTO Stats (Engineer, TotalTime)
    SELECT
        r.Engineer,
        SUM(r.Multiplier * w.Time) AS TotalTime
    FROM Reports r
    JOIN Works w ON r.Work = w.Name
    WHERE r.Date LIKE '__/03/2025%'
    Group By r.Engineer
""")

conn.commit()
conn.close()
