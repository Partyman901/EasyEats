from pstats import Stats
from re import S
import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime
import requests
import os
import sqlite3
from base import Base
from apscheduler.schedulers.background import BackgroundScheduler
from stats import Stats
from flask_cors import CORS, cross_origin

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

if os.path.exists("app_config['datastore']['filename']") != True:
    conn = sqlite3.connect("app_config['datastore']['filename']")
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

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine(f"sqlite:///{app_config['datastore']['filename']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def populate_stats():
    """ Periodically update stats """
    logger.info(f"Populate stats has started")
    current_date = datetime.datetime.now()
    format_date = current_date.strftime("%Y-%m-%dT%H:%M:%S")
    session = DB_SESSION()
    if os.path.isfile('stats.sqlite'):
        last_updated = session.query(Stats).order_by(Stats.last_updated.desc()).first()
        if last_updated == None:
            last_updated = {'num_orders': 0, 'num_deliveries': 0, 'max_price_purchase': 0, 'max_distance_delivery': 0, 'avg_price_purchase': 0, 'last_updated': '2020-02-16T16:18:47'}
            stats_list = [last_updated]
        else:
            last_updated = last_updated.to_dict()
            all_stats = session.query(Stats).order_by(Stats.last_updated.desc()).all()
            stats_list = []
            for stat in all_stats:
                stats_list.append(stat.to_dict())
    else:
        last_updated = {'num_orders': 0, 'num_deliveries': 0, 'max_price_purchase': 0, 'max_distance_delivery': 0, 'avg_price_purchase': 0, 'last_updated': '2020-02-16T16:18:47'}

    orders_data = requests.get(f"{app_config['eventstore']['url']}/orders", params = {"start_timestamp": last_updated["last_updated"], "end_timestamp":format_date})
    deliveries_data = requests.get(f"{app_config['eventstore']['url']}/deliveries", params = {"start_timestamp": last_updated["last_updated"], "end_timestamp":format_date})

    if orders_data.status_code and deliveries_data.status_code == 200:
        logger.info(f"Data received! {len(orders_data.json())} orders received, {len(deliveries_data.json())} deliveries received")
        for order in orders_data.json():
            logger.debug(f"Order data: {order['traceID']} received")
        for delivery in deliveries_data.json():
            logger.debug(f"Delivery data: {delivery['traceID']} received")

        num_orders = last_updated["num_orders"] + len(orders_data.json()) # Calculate stats

        num_deliveries = last_updated["num_deliveries"]  + len(deliveries_data.json())

        max_price_purchase = last_updated['max_price_purchase']
        for order in orders_data.json():
            if order['price'] > max_price_purchase:
                max_price_purchase = order['price']

        max_distance_delivery = last_updated['max_distance_delivery']
        for delivery in deliveries_data.json():
            if delivery['distance'] > max_distance_delivery:
                max_distance_delivery = delivery['distance']

        avg_price_purchase = 0
        for order in orders_data.json():
            avg_price_purchase += order['price']
        total_price_stat = 0
        for stat in stats_list:
            total_price_stat += stat['avg_price_purchase'] 

        total_price_stat += avg_price_purchase

        avg_price_purchase = total_price_stat / len(stats_list)

        last_updated = current_date

        stats = Stats(num_orders, num_deliveries, max_price_purchase, max_distance_delivery, avg_price_purchase, current_date)
        stats_dict = stats.to_dict()
        print(stats_dict)

        session.add(stats)
        session.commit()
        session.close()
        logger.info("Finished processing data")
    else:
        logger.error(f"Failed to receive data with error code: {orders_data.status_code} and {deliveries_data.status_code}")
    
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()

def get_stats():
    """ Get stats event """
    logger.info("get_stats request has started")
    session = DB_SESSION()
    last_updated = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if last_updated == None:
        logger.error("Statistics do not exist!")
    data_dict = last_updated.to_dict()
    logger.debug(f"Coverted to dictionary: {data_dict}")
    logger.info("get_stats requests has completed!")
    session.close()

    return data_dict, 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__== "__main__":
    init_scheduler()
    app.run(port=8100, debug=True)