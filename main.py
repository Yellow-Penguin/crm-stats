import sqlite3
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from modules import crm_api
from modules.upload_works import upload_works
from modules.upload_works_list import upload_work_list
app = Flask(__name__)

# Get login info from env
load_dotenv()
username = os.getenv("LOGIN_USERNAME")
passwd = os.getenv("LOGIN_PASSWORD")

driver = crm_api.start_and_login(username, passwd)


def get_reports(start_date=None, end_date=None):
    """Отримання звітів із БД"""
    conn = sqlite3.connect("works.db")
    cursor = conn.cursor()
    print(f'Start date: {start_date}, End date: {end_date}')
    if start_date and end_date:
        cursor.execute("""
            SELECT Engineer, SUM(Multiplier * Works.Time) 
            FROM Reports 
            JOIN Works ON Reports.Work = Works.Name
            WHERE Date BETWEEN ? AND ?
            GROUP BY Engineer
        """, (start_date, end_date))
    else:
        cursor.execute("""
            SELECT Engineer, SUM(Multiplier * Works.Time) 
            FROM Reports 
            JOIN Works ON Reports.Work = Works.Name
            WHERE strftime('%Y-%m', Date) = strftime('%Y-%m', 'now')  
            GROUP BY Engineer
        """)

    data = cursor.fetchall()
    conn.close()
    return data

def get_last_work():
    conn = sqlite3.connect("works.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT MAX(DATE) FROM REPORTS""")
    data = cursor.fetchone()[0]
    return data

@app.route("/", methods=["GET", "POST"])
def home():
    reports = []
    start_date = end_date = None
    date_choice = "current"
    last_work_date = get_last_work()

    if request.method == "POST":
        date_choice = request.form["date-choice"]
        if date_choice == "custom":
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")

        reports = get_reports(start_date, end_date if date_choice == "custom" else None)
    else:
        reports = get_reports()

    return render_template("index.html", reports=reports, start_date=start_date, end_date=end_date,
                           date_choice=date_choice, last_work_date=last_work_date)


@app.route("/update_reports", methods=["POST"])
def update_reports():
    """Оновлення бази даних і повернення оновлених даних"""
    action_type = request.get_json().get("action")
    print(f'Action type: {action_type}')
    if action_type == "report":
        crm_api.download_report(driver)
        res = upload_works()
        if res != 0:
            print("Error in upload_works")
    elif action_type == "work-list":
        crm_api.download_work_list(driver)
        res = upload_work_list()
        if res != 0:
            print("Error in upload_work_list")
    updated_reports = get_reports()
    return jsonify(updated_reports)

if __name__ == "__main__":

    app.run(
        debug=True, passthrough_errors=True,
        use_debugger=True, use_reloader=True
    )

