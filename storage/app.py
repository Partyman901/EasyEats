import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime
import json

from threading import Thread
from pykafka.common import OffsetType
from pykafka import KafkaClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from delivery import Delivery
from order import Order

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

logger = logging.getLogger('basicLogger')
DB_ENGINE = create_engine(f"mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
# BRUH =  mysql+pymysql://root:P@ssw0rd!>@localhost:3306/events


def getOrder(timestamp):
    """ Gets a order event """
    session = DB_SESSION()
    logger.info(f"Connected to DB. Hostname: {hostname}, Port: {port}")
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    orders = session.query(Order).filter(Order.date_created >= timestamp_datetime)
    results_list = []

    for order in orders:
        results_list.append(order.to_dict())

    session.close()

    logger.info("Query for Orders after %s returns %d results" %(timestamp, len(results_list)))
    return results_list, 200

def getDelivery(timestamp):
    """ Gets a delivery event """
    session = DB_SESSION()
    logger.info(f"Connected to DB. Hostname: {hostname}, Port: {port}")
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    deliveries = session.query(Delivery).filter(Delivery.date_created >= timestamp_datetime)
    results_list = []

    for delivery in deliveries:
        results_list.append(delivery.to_dict())

    session.close()

    logger.info("Query for Deliveries after %s returns %d results" %(timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    """ Process event messages """
    logger.info(f"Started Processing Messages!")
    hostname = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
    client = KafkaClient(hosts=hostname)
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


# def addOrder(body):
#     """ Adds order event """
#     # body_string = f"Customer: {body['customer']}, Food: {body['food']}, Price: {body['price']}, OrderID: {body['orderID']}"
#     # add_json(body_string)
#     session = DB_SESSION()
#     logger.info(f"Connected to DB. Hostname: {hostname}, Port: {port}")
#     order = Order(body['customer'],
#                     body['food'],
#                     body['orderID'],
#                     body['price'],
#                     body['traceID'])
#     session.add(order)
#     session.commit()
#     session.close()
#     logger.debug(f"Stored event addOrder request with a trace id of {body['traceID']}")
#     return NoContent, 201


# def addDelivery(body):
#     """ Adds delivery event """
#     # body_string = f"orderNum: {body['orderNum']}, Distance: {body['distance']}, Driver: {body['driver']}, Address: {body['address']}"
#     # add_json(body_string)
#     session = DB_SESSION()
#     logger.info(f"Connected to DB. Hostname: {hostname}, Port: {port}")
#     delivery = Delivery(body['address'],
#                     body['driver'],
#                     body['distance'],
#                     body['orderNum'],
#                     body['traceID'])
#     session.add(delivery)

#     session.commit()
#     session.close()
#     logger.debug(f"Stored event addDelivery request with a trace id of {body['traceID']}")
#     return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__== "__main__":
    t1 = Thread(target=process_messages)
    logger.info(f"t1 = {t1}")
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, debug=True)