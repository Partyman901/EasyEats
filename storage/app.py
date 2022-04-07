import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime
import json
import time

from threading import Thread
from pykafka.common import OffsetType
from pykafka import KafkaClient
from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from base import Base
from delivery import Delivery
from order import Order
import os

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

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

DB_ENGINE = create_engine(f"mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
# BRUH =  mysql+pymysql://root:P@ssw0rd!>@localhost:3306/events


def getOrder(start_timestamp, end_timestamp):
    """ Gets a order event """
    session = DB_SESSION()
    logger.info(f"Connected to DB. Hostname: {hostname}, Port: {port}")
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")
    orders = session.query(Order).filter(Order.date_created >= start_timestamp_datetime, Order.date_created < end_timestamp_datetime)
    results_list = []

    for order in orders:
        results_list.append(order.to_dict())

    session.close()

    logger.info("Query for Orders after %s and before %s returns %d results" %(start_timestamp, end_timestamp, len(results_list)))
    return results_list, 200

def getDelivery(start_timestamp, end_timestamp):
    """ Gets a delivery event """
    session = DB_SESSION()
    logger.info(f"Connected to DB. Hostname: {hostname}, Port: {port}")
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")
    deliveries = session.query(Delivery).filter(Delivery.date_created >= start_timestamp_datetime, Delivery.date_created < end_timestamp_datetime)
    results_list = []

    for delivery in deliveries:
        results_list.append(delivery.to_dict())

    session.close()

    logger.info("Query for Deliveries after %s and before %s returns %d results" %(start_timestamp, end_timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    """ Process event messages """
    logger.info(f"Started Processing Messages!")
    hostname = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
    retry_count = 0
    while retry_count < app_config["events"]["retries"]:
        logger.info(f"Trying to Connect to Kafka on retry count {retry_count}")
        try:
            client = KafkaClient(hosts=hostname)
            retry_count = app_config["events"]["retries"]
        except Exception as e:
            logger.error(f"Connection Failed! Error: {e}")
            time.sleep(app_config["events"]["sleep_time"])
            retry_count += 1

    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        
        body = msg["payload"]

        if msg["type"] == "order":
            session = DB_SESSION()
            logger.info(f"Connected to DB. Hostname: {hostname}, Port: {port}")
            order = Order(body['customer'],
                            body['food'],
                            body['orderID'],
                            body['price'],
                            body['traceID'])
            session.add(order)
            session.commit()
            session.close()
            logger.debug(f"Stored event addOrder request with a trace id of {body['traceID']}")
        elif msg["type"] == "delivery":
            session = DB_SESSION()
            logger.info(f"Connected to DB. Hostname: {hostname}, Port: {port}")
            delivery = Delivery(body['address'],
                            body['driver'],
                            body['distance'],
                            body['orderNum'],
                            body['traceID'])
            session.add(delivery)

            session.commit()
            session.close()
            logger.debug(f"Stored event addDelivery request with a trace id of {body['traceID']}")
        consumer.commit_offsets()

    logger.debug(f"Stored event addOrder request with a trace id of {body['traceID']}")


def get_health():
    """ Returns 200 """
    return { "message": "Healthy!"}, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",base_path="/storage",strict_validation=True, validate_responses=True)

if __name__== "__main__":
    t1 = Thread(target=process_messages)
    logger.info(f"t1 = {t1}")
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, debug=True)