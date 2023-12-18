from flask import Flask
import sqlite3 

app = Flask(__name__)


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
    app.run(debug=True)