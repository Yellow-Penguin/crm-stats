import time
from pathlib import Path
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from log_config import logger

report_path = Path.cwd() / "downloads"

def start_and_login(username, passwd):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    # Set default path to download reports
    prefs = {"download.default_directory": str(report_path)}
    options.add_experimental_option("prefs", prefs)
    # Initialize the WebDriver (ensure chromedriver is properly installed and added to PATH)
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://web.remonline.app/login")
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.NAME, "login"))).send_keys(username)
        wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(passwd)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".PsVN1"))).click()
        wait.until(EC.url_changes(driver.current_url))
        #logger.info("CRM LOGIN SUCCESS")
    except Exception as e:
        #logger.error(f'CRM LOGIN FAILED due to {e}')
        return -2
    finally:
        return driver

def download_report(driver):
    try:
        # Download report for this month
        driver.get("https://web.remonline.app/reports/orders/services")
        wait = WebDriverWait(driver, 30)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".qJgSk"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".mi3FM.Sbo0b.RKBw5.pnoBQ.z0cnO"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".wFyif"))).click()
    except Exception as e:
        #logger.error(f'CRM REPORT DOWNLOAD FAILED due to {e}:')
        return -2
    finally:
        # Rename downloaded report to format "Report-month-year"
        report = report_path.joinpath("Labors and Services Report.xls")
        new_report = report.with_name("Report" + date.today().strftime("-%m-%Y") + ".xls")
        while not report.exists():
            time.sleep(0.2)
        if new_report.exists():
            new_report.unlink()
        report.rename(new_report)
        #logger.info("CRM REPORT DOWNLOAD SUCCESSFUL")
        # Close browser
        #driver.quit()
        return driver

def download_work_list(driver):
    try:
        # Download work list
        driver.get("https://web.remonline.app/company/services-pricelist")
        wait = WebDriverWait(driver, 30)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='All labors and services']"))).click()
        #wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "//div[contains(@class, 'NHCVN')]//span[text()='Дрони']"))).move_to_element().click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[div[contains(text(), 'Export')]]"))).click()
    except Exception as e:
        #logger.error(f'CRM WORKS LIST DOWNLOAD FAILED due to {e}:')
        return -2
    finally:
        work_list = report_path.joinpath("Labors and Services.xls")
        new_work_list = work_list.with_name("works_list.xls")
        while not work_list.exists():
            time.sleep(0.2)
        if new_work_list.exists():
            new_work_list.unlink()
        work_list.rename(new_work_list)
        #logger.info("CRM WORKS LIST DOWNLOAD SUCCESSFUL")
        # Close browser
        #driver.quit()
        return driver
















