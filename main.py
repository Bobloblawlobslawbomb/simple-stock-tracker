import os
from os.path import join, dirname
from datetime import date, timedelta
import requests
from twilio.rest import Client
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

stock_api_key = os.environ.get('STOCK_API_KEY')
news_api_key = os.environ.get('NEWS_API_KEY')
account_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN')
phone_from = os.environ.get('PHONE_FROM')
phone_to = os.environ.get('PHONE_TO')

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
PERCENTAGE_THRESHOLD = 1

URL = "https://www.alphavantage.co/query"
NEWS_URL = "https://newsapi.org/v2/everything"

stock_params = {
    'function': "TIME_SERIES_DAILY",
    'symbol': STOCK,
    'apikey': stock_api_key
}

r = requests.get(URL, params=stock_params)
r.raise_for_status()
data = r.json()

today = str(date.today())
yesterday = str(date.today() - timedelta(days=1))
day_before_yesterday = str(date.today() - timedelta(days=2))

news_params = {
    'q': COMPANY_NAME,
    'from': today,
    'sortBy': "popularity",
    'apiKey': news_api_key
}

yesterday_close = float(data['Time Series (Daily)'][yesterday]['4. close'])

db_yesterday_close = float(
    data['Time Series (Daily)'][day_before_yesterday]['4. close'])

diff = round(yesterday_close - db_yesterday_close, 4)
percent_diff = round(diff / db_yesterday_close * 100)

if percent_diff > 0:
    percent_diff_str = "🔺" + str(percent_diff)
else:
    percent_diff_str = str(percent_diff).replace("-", "🔻")
    percent_diff = percent_diff * -1

if percent_diff >= PERCENTAGE_THRESHOLD:
    response = requests.get(NEWS_URL, params=news_params)
    response.raise_for_status()
    news_data_all = response.json()["articles"]

    three_articles = news_data_all[:3]

    formatted_articles = [
        f"{STOCK}: {percent_diff_str}%\nHeadline {article['title']}.\nBrief : {article['description']}" for article in three_articles]

    client = Client(account_sid, auth_token)

    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_=phone_from,
            to=phone_to
        )
