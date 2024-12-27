from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from flask import Flask, render_template
import time
import uuid

# ProxyMesh settings
proxy_host = ""
proxy_port = ""
proxy_user = ""
proxy_password = ""

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['twitter_trends']
collection = db['trending_topics']

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    # Selenium Setup
    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server=http://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://twitter.com/login")
        time.sleep(5) 

        driver.find_element(By.NAME, "session[username_or_email]").send_keys("TWITTER_USERNAME")
        driver.find_element(By.NAME, "session[password]").send_keys("TWITTER_PASSWORD")
        driver.find_element(By.CSS_SELECTOR, "div[data-testid='LoginForm_Login_Button']").click()
        time.sleep(10)

        driver.get("https://twitter.com/explore")
        time.sleep(5)

        trends = driver.find_elements(By.XPATH, "//div[@data-testid='trend']")[:5]
        trend_names = [trend.text for trend in trends]

        unique_id = str(uuid.uuid4())
        current_ip = proxy_host  # Replace with a method to fetch IP
        record = {
            "_id": unique_id,
            "nameoftrend1": trend_names[0] if len(trend_names) > 0 else None,
            "nameoftrend2": trend_names[1] if len(trend_names) > 1 else None,
            "nameoftrend3": trend_names[2] if len(trend_names) > 2 else None,
            "nameoftrend4": trend_names[3] if len(trend_names) > 3 else None,
            "nameoftrend5": trend_names[4] if len(trend_names) > 4 else None,
            "datetime": time.strftime('%Y-%m-%d %H:%M:%S'),
            "ip_address": current_ip
        }
        collection.insert_one(record)

        #HTML Output to render
        html = f"""
        <html>
        <body>
            <h3>These are the most happening topics as on {record['datetime']}:</h3>
            <ul>
                <li>{record['nameoftrend1']}</li>
                <li>{record['nameoftrend2']}</li>
                <li>{record['nameoftrend3']}</li>
                <li>{record['nameoftrend4']}</li>
                <li>{record['nameoftrend5']}</li>
            </ul>
            <p>The IP address used for this query was {record['ip_address']}.</p>
            <h3>JSON extract from MongoDB:</h3>
            <pre>{record}</pre>
            <a href="/">Click here to run the query again</a>
        </body>
        </html>
        """
        return html

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
