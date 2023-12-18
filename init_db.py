import sqlite3


def init_db():
    conn = sqlite3.connect('stock_data.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''CREATE TABLE stocks
                   (symbol TEXT PRIMARY KEY, shares INTEGER, price REAL, last_updated TIMESTAMP)''')
    
    # Insert initial stock data
    stocks = [('TSLA', 16, 0, None), ('GOOGL', 20, 0, None),
              ('AMZN', 20, 0, None), ('AAPL', 13, 0, None),
              ('CSCO', 1, 0, None), ('NOK', 2, 0, None)]
    cursor.executemany('INSERT INTO stocks VALUES (?, ?, ?, ?)', stocks)

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()


if __name__ == '__main__':
    init_db()