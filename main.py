from playwright.sync_api import Playwright, sync_playwright
from mysqlConnection import DatabaseConnection
from dotenv import load_dotenv
from lxml import html
from datetime import datetime
import time
import os

def run(playwright: Playwright, url : str) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    calenders = []
    page.evaluate('window.scrollTo(0, 5000);')
    for _ in range(12):
        calender = page.locator('div.calendar')
        calenders.append(calender.inner_html())
        page.get_by_role("button", name="Next month").click()
        time.sleep(1)

    context.close()
    browser.close()
    return calenders

if __name__ == "__main__":
    load_dotenv()
    url = "https://www.vrbo.com/1753814"
    with sync_playwright() as playwright:
        calenders = run(playwright, url)

    values = []
    for calender in calenders:
        etree = html.fromstring(calender)
        months = etree.xpath("//div[@class='month multi simple']")
        for month in months:
            date_month = month.xpath("h4/span")[0].text
            items = month.xpath("table/tbody/tr/td/div/div/div[2]")
            for item in items:
                day = item.xpath("div[1]")[0].text
                try:
                    price = item.xpath("div[2]")[0].text
                except:
                    price = None
                date = day + " " + date_month
                date = datetime(2025, 2, 28, 0, 0)
                values.append((date, price))
    
    connection = DatabaseConnection(os.environ.get("DB_USERNAME"), os.environ.get("DB_PASSWORD"), os.environ.get("DB_NAME"))
    connection.connection()
    query = """ insert into availability_date_price(date, price) values(%s, %s); """
    connection.cursor.executemany(query, values)
    connection.db.commit()
    print("Data Inserted in Db")
    connection.close_connection()
    print("Program Executed. Exiting....")