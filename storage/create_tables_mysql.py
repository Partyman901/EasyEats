import mysql.connector 
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_conn = mysql.connector.connect(host=app_config['datastore']['hostname'], user=app_config['datastore']['user'], 
password=app_config['datastore']['password'], database=app_config['datastore']['db']) 
 
 
db_cursor = db_conn.cursor()
db_cursor.execute(''' 
          CREATE TABLE orders
          (id INT NOT NULL AUTO_INCREMENT, 
           customer VARCHAR(250) NOT NULL,
           food VARCHAR(250) NOT NULL,
           orderID INTEGER NOT NULL,
           price INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           traceID VARCHAR(100) NOT NULL,
           CONSTRAINT orders_pk PRIMARY KEY (id)) 
          ''') 
 
db_cursor.execute(''' 
          CREATE TABLE deliveries
          (id INT NOT NULL AUTO_INCREMENT, 
           address VARCHAR(250) NOT NULL,
           driver VARCHAR(250) NOT NULL,
           distance INTEGER NOT NULL,
           orderNum INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           traceID VARCHAR(100) NOT NULL,
           CONSTRAINT deliveries_pk PRIMARY KEY (id)) 
          ''') 
 
db_conn.commit() 
db_conn.close() 
