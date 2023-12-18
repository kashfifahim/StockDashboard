from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import requests
import sqlite3 

app = Flask(__name__)


def schedule_stock_updates():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_all_stocks, trigger="interval", minutes=15)
    scheduler.start()


def update_all_stocks():
    api_key = 'Z26IND1A7LZTHK7V'
    symbols = ['TSLA', 'GOOGL', 'AMZN', 'AAPL', 'CSCO', 'NOK']
    for symbol in symbols:
        price = fetch_stock_price(symbol, api_key)
        update_stock_price(symbol, price)


def fetch_stock_price(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    price = data["Global Quote"]["05. price"]
    return float(price)


def update_stock_price(symbol, price):
    conn = get_db_connection()
    conn.execute('UPDATE stocks SET PRICE = ?, last_update = CURRENT_TIMESTAMP WHERE symbol = ?', (price, symbol))
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('stock_data.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/update-stock')
def update_stock():
    # function to update stock prices
    # will replace with real data fetching logic
    conn = get_db_connection()
    conn.execute('UPDATE stocks SET price = 1000 WHERE symbol = "TESLA"')
    conn.commit()
    conn.close()
    return "Stock updated"


@app.route('/stocks')
def stocks():
    conn = get_db_connection()
    stocks = conn.execute('SELECT * FROM stocks').fetchall()
    conn.close()
    return {'stocks': [dict(row) for row in stocks]}


if __name__ == '__main__':
    schedule_stock_updates()
    app.run(debug=True)