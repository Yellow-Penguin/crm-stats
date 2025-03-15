import sqlite3
import pandas as pd
from datetime import date
from pathlib import Path

# TODO: FIX PATH`S
report_path = Path.cwd() / "downloads"
report = report_path.joinpath("Report" + date.today().strftime("-%m-%Y") + ".xls")
#report = report_path.joinpath("Report-02-2025.xls")

def upload_works():
    # Open Excel report
    df = pd.read_excel(report)
    # Open database
    conn = sqlite3.connect('works.db', timeout=10)
    cursor = conn.cursor()

    #   Table of reports for all months
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reports (
            Date TEXT NOT NULL, 
            Engineer TEXT NOT NULL,
            OrderId TEXT,
            Work TEXT NOT NULL,
            Multiplier REAL NOT NULL,
            Price INTEGER,
            FOREIGN KEY(Work) REFERENCES Works(Name),
            UNIQUE(Date, Engineer, OrderId, Work)
        )
    """)

    try:
        #   Temporary table
        cursor.execute("""
            CREATE TEMPORARY TABLE temp_reports (
                Date TEXT,
                Engineer TEXT,
                OrderId TEXT,
                Work TEXT,
                Multiplier REAL,
                Price INTEGER
            )
        """)
        # Insert data from Excel report to db table
        for i, row in df.iterrows():
                formatted_date = row['Date and time'].strftime('%Y-%m-%d %H:%M:%S')
                if isinstance(row['Quantity'], str):
                    float_multiplier = float(row['Quantity'].replace(',', '.'))
                else:
                    float_multiplier = row['Quantity']
                cursor.execute("""
                    INSERT INTO temp_reports (Date, Engineer, OrderId, Work, Multiplier, Price)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (formatted_date, row['Technician'], row['Ticket #'], row['Service/Labor'], float_multiplier, row['Amount, ₴'])
                )
        # Delete from db works which not in excel report
        # (In case if someone deleted work in CRM, which was added to db)
        # TODO: change dates automatically
        cursor.execute("""
                DELETE FROM Reports
                WHERE strftime('%Y-%m', Date) = strftime('%Y-%m', 'now')
                And (Date, Engineer, OrderId, Work, Multiplier) NOT IN (
                    SELECT Date, Engineer, OrderId, Work, Multiplier FROM temp_reports
                );
            """)
        # Insert works, which was not deleted in db Report table without duplication
        cursor.execute("""
                INSERT OR IGNORE INTO Reports (Date, Engineer, OrderId, Work, Multiplier, Price)
                SELECT Date, Engineer, OrderId, Work, Multiplier, Price FROM temp_reports;
            """)
    except Exception as e:
        print('Error in upload_works:\n', e)
        return -1
    finally:
        conn.commit()
        conn.close()

    return 0