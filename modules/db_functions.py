import logging
from datetime import datetime
import sqlite3
import pandas as pd
from datetime import date
from pathlib import Path
#from log_config import logger

download_path = Path.cwd() / "downloads"
report = download_path.joinpath("Report" + date.today().strftime("-%m-%Y") + ".xls")
work_list = download_path.joinpath("works_list.xls")

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
            UNIQUE(Date, Engineer, OrderId, Work),
            ORDER BY Date DESC;
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
        #logger.error(f"Loading Works to db failed: {e}")
        return -1
    finally:
        #logger.info("Loading Works to db finished")
        conn.commit()
        conn.close()
    return 0

def upload_work_list():
    # Delete all works that not in "Drones" category
    df = pd.read_excel(work_list)
    df = df[df["Category"] == "Дрони"]
    df = df[["Name", "Duration (minutes)"]]

    #df.to_excel("works_list_test.xlsx")

    # Open database
    conn = sqlite3.connect('works.db', timeout=10)
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
        #logger.error(f"Loading Works List to db failed: {e}")
        return -1
    finally:
        #logger.info("Loading Works List to db finished")
        conn.commit()
        conn.close()
    return 0

def get_reports(start_date=None, end_date=None):
    conn = sqlite3.connect("works.db")
    cursor = conn.cursor()
    try:
        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            cursor.execute("""
                SELECT Engineer, ROUND(SUM(Multiplier * Works.Time), 3) 
                FROM Reports 
                JOIN Works ON Reports.Work = Works.Name
                WHERE Date BETWEEN ? AND ?
                GROUP BY Engineer
            """, (start_datetime, end_datetime))
        else:
            cursor.execute("""
                SELECT Engineer, ROUND(SUM(Multiplier * Works.Time), 3) 
                FROM Reports 
                JOIN Works ON Reports.Work = Works.Name
                WHERE strftime('%Y-%m', Date) = strftime('%Y-%m', 'now')  
                GROUP BY Engineer
            """)
    except Exception as e:
        #logger.error(f"Failed to retrieve statistics from the database: {e}")
        return -1
    finally:
        #logger.info(f"Retrieving statistics from the database, start date - {start_date} and end date - {end_date}")
        data = cursor.fetchall()
        conn.close()
        return data

def get_last_work():
    conn = sqlite3.connect("works.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT MAX(DATE) FROM REPORTS""")
    except Exception as e:
        #logger.error(f"Unsuccessful obtaining of the last work date: {e}")
        return -1
    finally:
        data = cursor.fetchone()[0]
        #logger.info(f"Last work date retrieved - {data}")
        return data