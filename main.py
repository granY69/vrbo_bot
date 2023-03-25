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
        calender_html = calender.inner_html()
        calenders.append(calender_html)
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
            tds = month.xpath("table/tbody/tr/td[contains(@aria-label,'') and @aria-hidden='false']")
            for td in tds:
                date_text = td.xpath("@aria-label")[0]
                is_available = "inavailable"
                price = None
                if not " is unavailable." in date_text:
                    try:
                        price = td.xpath("div/div/div[2]/div[2]")[0].text
                        is_available = "available"
                    except:
                        pass
                date_obj = datetime.strptime(date_text.replace(" is unavailable.", ""), "%B %d, %Y")
                values.append((url, date_obj, is_available, price))
    
    connection = DatabaseConnection(os.environ.get("DB_USERNAME"), os.environ.get("DB_PASSWORD"), os.environ.get("DB_NAME"), os.environ.get("DB_HOST"))
    connection.connection()
    query = """ insert into availability_date_price(url, date, is_available, price) values(%s, %s, %s, %s); """
    connection.cursor.executemany(query, values)
    connection.db.commit()
    print("Data Inserted in Db")
    connection.close_connection()
    print("Program Executed. Exiting....")