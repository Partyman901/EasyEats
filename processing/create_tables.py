import sqlite3
conn = sqlite3.connect('stats.sqlite')
c = conn.cursor()
c.execute('''
    CREATE TABLE stats
    (id INTEGER PRIMARY KEY ASC,
    num_orders INTEGER NOT NULL,
    num_deliveries INTEGER NOT NULL,
    max_price_purchase INTEGER,
    max_distance_delivery INTEGER,
    avg_price_purchase INTEGER,
    last_updated VARCHAR(100) NOT NULL)
    ''')
conn.commit()
conn.close() 