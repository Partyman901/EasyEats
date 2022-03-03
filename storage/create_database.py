import sqlite3

conn = sqlite3.connect('kafkalmao.eastus.cloudapp.azure.com')

c = conn.cursor()

c.execute('''
          CREATE TABLE orders
          (id INTEGER PRIMARY KEY ASC, 
           customer VARCHAR(250) NOT NULL,
           food VARCHAR(250) NOT NULL,
           orderID INTEGER NOT NULL,
           price INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           traceID VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE deliveries
          (id INTEGER PRIMARY KEY ASC, 
           address VARCHAR(250) NOT NULL,
           driver VARCHAR(250) NOT NULL,
           distance INTEGER NOT NULL,
           orderNum INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           traceID VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
