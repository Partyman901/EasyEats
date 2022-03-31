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
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin
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

def get_order(index): 
    """ Get order Reading in History """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 

    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000) 
 
    logger.info("Retrieving order at index %d" % index) 
    try: 
        print(consumer)
        msg_list = []
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            logger.debug(f"MSG = {msg} at index")
            if msg["type"] == 'order':
                msg_list.append(msg)
        return msg_list[index], 200
    except Exception as e: 
        logger.error(f"No more messages found: {e}") 
     
    logger.error("Could not find order at index %d" % index) 
    return { "message": "Not Found"}, 404


def get_delivery(index): 
    """ Get delivery Reading in History """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000) 
 
    logger.info("Retrieving order at index %d" % index) 
    try: 
        msg_list = []
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            logger.debug(f"MSG = {msg}")
            event = msg
            if msg["type"] == 'delivery':
                msg_list.append(msg)
        return msg_list[index], 200
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find delivery at index %d" % index) 
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path="/audit_log", strict_validation=True, validate_responses=True)

if __name__== "__main__":
    app.run(port=8110, debug=True)