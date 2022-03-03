import sqlite3

conn = sqlite3.connect('easyeatsdb.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE orders
          ''')
c.execute('''
          DROP TABLE deliveries
          ''')

conn.commit()
conn.close()
