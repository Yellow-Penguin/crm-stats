import hashlib
import os
from waitress import serve
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from modules import crm_api
from modules import db_functions as dbf
#from modules.log_config import logger
app = Flask(__name__)

# Get login info from env
load_dotenv()
username = os.getenv("LOGIN_USERNAME")
passwd = os.getenv("LOGIN_PASSWORD")
admin_passwd = os.getenv("ADMIN_PASSWORD")

driver = crm_api.start_and_login(username, passwd)

""""@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")"""

"""@app.errorhandler(500)
def handle_500(error):
    logger.error(f"Error 500: {error}, URL: {request.url}")
    return "Server Error", 500"""
@app.route("/", methods=["GET", "POST"])
def home():
    reports = []
    start_date = end_date = None
    date_choice = "current"
    last_work_date = dbf.get_last_work()

    if request.method == "POST":
        date_choice = request.form["date-choice"]
        if date_choice == "custom":
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")

        reports = dbf.get_reports(start_date, end_date if date_choice == "custom" else None)
    else:
        reports = dbf.get_reports()

    return render_template("index.html", reports=reports, start_date=start_date, end_date=end_date,
                           date_choice=date_choice, last_work_date=last_work_date)


@app.route("/update_reports", methods=["POST"])
def update_reports():
    action_type = request.get_json().get("action")
    if action_type == "report":
        crm_api.download_report(driver)
        res = dbf.upload_works()
    elif action_type == "work-list":
        crm_api.download_work_list(driver)
        res = dbf.upload_work_list()
    updated_reports = dbf.get_reports()
    last_work_date = dbf.get_last_work()
    return jsonify(updated_reports)

# TODO: Login
@app.route("/admin_login", methods=["GET", "POST"])
def admin_functions():
    if request.method == "POST":
        entered_pass = request.form["password"]
        hs = hashlib.sha256(entered_pass.encode('utf-8')).hexdigest()
        print(f'Hash: hs')
        if hs == admin_passwd:
            return render_template("admin_page.html")
        else:
            return "Nope"
    return  render_template("admin_login.html")



if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)

