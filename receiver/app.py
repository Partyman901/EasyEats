from email.headerregistry import ContentTypeHeader
import connexion
from connexion import NoContent
import json
import datetime
import requests
import sys
import yaml
import logging
import logging.config
import uuid
import time
from pykafka import KafkaClient
from order import Order
from delivery import Delivery
import os
MAX_EVENTS = 10
EVENT_FILE = "data.json"

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


def addOrder(body):
    """ Adds order event """
    traceID = str(uuid.uuid4())
    body['traceID'] = traceID
    # client = KafkaClient(
    #     hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    logger.info(f"CLIENT = {client}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    logger.info(f"TOPIC = {topic.name}")
    producer = topic.get_sync_producer()
    logger.info(f"PRODUCER = {producer}")
    msg = {"type": "order", "datetime": datetime.datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S"), "payload": body}
    msg_str = json.dumps(msg)
    logger.info(f"MSG = {msg_str}")
    producer.produce(message=msg_str.encode('utf-8'))
    # value = requests.post(app_config['orderevent']['url'], json=body, headers={"Content-Type": "application/json"})
    logger.info(
        f"Returned event addOrder response with (id: {body['traceID']} with status 201")
    return NoContent, 201


def addDelivery(body):
    """ Adds delivery event """
    traceID = str(uuid.uuid4())
    body['traceID'] = traceID
    # client = KafkaClient(
    #     hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    logger.info(
        f"Received event addOrder request with a trace id of {body['traceID']}")
    msg = {"type": "delivery", "datetime": datetime.datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S"), "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(message=msg_str.encode('utf-8'))
    # value = requests.post(app_config['deliveryevent']['url'], json=body, headers={"Content-Type": "application/json"})
    logger.info(
        f"Returned event addOrder response with (id: {body['traceID']} with status 201")
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/receiver", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
