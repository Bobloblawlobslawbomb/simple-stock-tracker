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
PERCENTAGE_THRESHOLD = 5

url = F'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={stock_api_key}'
news_url = "https://newsapi.org/v2/everything"

r = requests.get(url)
r.raise_for_status()
data = r.json()

today = str(date.today())
yesterday = str(date.today() - timedelta(days=1))
day_before_yesterday = str(date.today() - timedelta(days=2))

news_params = {
    'q': "Tesla",
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
    response = requests.get(news_url, params=news_params)
    response.raise_for_status()
    news_data_all = response.json()["articles"]

    news_data_one_title = news_data_all[0]["title"]
    news_data_one_desc = news_data_all[0]["description"]

    news_data_two_title = news_data_all[1]["title"]
    news_data_two_desc = news_data_all[1]["description"]

    news_data_three_title = news_data_all[2]["title"]
    news_data_three_desc = news_data_all[2]["description"]

    client = Client(account_sid, auth_token)

    message_one = client.messages \
        .create(
            body=f"\n{STOCK}: {percent_diff_str}%\nHeadline: {news_data_one_title}\nBrief: {news_data_one_desc}",
            from_=phone_from,
            to=phone_to
        )
    message_two = client.messages \
        .create(
            body=f"\n{STOCK}: {percent_diff_str}%\nHeadline: {news_data_two_title}\nBrief: {news_data_two_desc}",
            from_=phone_from,
            to=phone_to
        )
    message_three = client.messages \
        .create(
            body=f"\n{STOCK}: {percent_diff_str}%\nHeadline: {news_data_three_title}\nBrief: {news_data_three_desc}",
            from_=phone_from,
            to=phone_to
        )
