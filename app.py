from flask import Flask, render_template
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import requests
import json
import os
import time


app = Flask(__name__)


load_dotenv()
# Alpha Vantage API details
API_URL = "https://www.alphavantage.co/query"
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")


# Caching
CACHE_DIR = "cache"
CACHE_DURATION = 3600


def cache_filename(symbol):
    try:
        return os.path.join(CACHE_DIR, f"{symbol}.json")
    except Exception as e:
        print(f"Error generating cache filename for symbol {symbol}: {e}")
        return None


def is_cache_valid(filename):
    try:
        if not os.path.exists(filename):
            return False

        now = datetime.now(pytz.timezone('US/Eastern'))
        if not (9 <= now.hour < 17):  # Check if current time is between 9 AM and 5 PM EST
            return True  # Outside trading hours, consider cache always valid

        file_mod_time = datetime.fromtimestamp(os.path.getmtime(filename))
        file_mod_time = file_mod_time.replace(tzinfo=pytz.timezone('US/Eastern'))

        # Check if cache is older than 30 minutes
        if now - file_mod_time > timedelta(minutes=30):
            return False

        return True
    except Exception as e:
        print(f"Error checking cache validity for file {filename}: {e}")
        return False


def read_cache(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def write_cache(filename, data):
    cache_data = {
        "price": data,
        "timestamp": time.time()
    }
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(filename, 'w') as file:
        json.dump(cache_data, file)


stocks = {
    "TSLA": 16,
    "GOOGL": 20,
    "AMZN": 20,
    "AAPL": 14,
    "CSCO": 1,
    "NOK": 2
}


def get_stock_prices(symbol):
    filename = cache_filename(symbol)

    try:
        # Attempt to make an API call first
        response = requests.get(API_URL, {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": API_KEY
        })
        response.raise_for_status()  # Raises an error for bad status codes
        data = response.json()

        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price = float(data["Global Quote"]["05. price"])
            # Successful API call, write data to cache
            write_cache(filename, price)
            return price, time.time()
        else:
            # Data not in expected format, fallback to cache
            print(f"Unexpected data format for {symbol}: {data}")
            cache_data = read_cache(filename) if os.path.exists(filename) else {"price": None}
            return cache_data["price"], cache_data.get("timestamp")

    except requests.exceptions.RequestException as e:
        # API call failed, fallback to cache
        print(f"Request error for symbol {symbol}: {e}")
        cache_data = read_cache(filename) if os.path.exists(filename) else {"price": None}
        return cache_data["price"], cache_data.get("timestamp")
    except Exception as e:
        print(f"An unexpected error occurred for symbol {symbol}: {e}")
        return None, None


def convert_utc_to_est(utc_timestamp):
    """Converts UTC timestamp to EST and formats it."""
    if utc_timestamp:
        utc_time = datetime.utcfromtimestamp(utc_timestamp).replace(tzinfo=pytz.utc)
        est_time = utc_time.astimezone(pytz.timezone('US/Eastern'))
        return est_time.strftime('%Y-%m-%d %I:%M %p EST')
    return "N/A"


def refresh():
    total_portfolio_value = 0
    stock_prices = {}
    last_updated_times = {}

    # Process each stock in the portfolio
    for symbol, quantity in stocks.items():
        # Retrieve the current price and timestamp for each stock
        current_price, timestamp = get_stock_prices(symbol)

        # Update stock prices and format timestamps
        stock_prices[symbol] = current_price if current_price is not None else "N/A"
        last_updated_times[symbol] = convert_utc_to_est(timestamp)

        # Calculate the total value of the portfolio
        if current_price is not None:
            total_portfolio_value += current_price * quantity

    return total_portfolio_value, stock_prices, last_updated_times


@app.route('/')
def index():
    total_portfolio_value, stock_prices, last_updated_times = refresh()
    return render_template("index.html", prices=stock_prices, total=total_portfolio_value, stocks=stocks, timestamps=last_updated_times)