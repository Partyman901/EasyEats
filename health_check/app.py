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
from check import Check
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

APPCONFILE = "app_conf.yml"
LOGCONFILE = "log_conf.yml"

with open(APPCONFILE, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(LOGCONFILE, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % APPCONFILE)
logger.info("Log Conf File: %s" % LOGCONFILE)

def get_health_checks():
    """ Periodically get health checks on services """
    logger.info(f"Checking health of services...")
    current_date = datetime.datetime.now()
    session = DB_SESSION()

    receiver_request = requests.get(f"{app_config['eventstore']['url']}{app_config['eventstore']['receiver']}", timeout=5)
    storage_request = requests.get(f"{app_config['eventstore']['url']}{app_config['eventstore']['storage']}", timeout=5)
    processing_request = requests.get(f"{app_config['eventstore']['url']}{app_config['eventstore']['processing']}", timeout=5)
    audit_request = requests.get(f"{app_config['eventstore']['url']}{app_config['eventstore']['audit']}", timeout=5)

    logger.info(f"Request received! Status code for Receiver is {receiver_request.status_code}")
    logger.info(f"Request received! Status code for Storage is {storage_request.status_code}")
    logger.info(f"Request received! Status code for Processing is {processing_request.status_code}")
    logger.info(f"Request received! Status code for Audit Log is {audit_request.status_code}")

    if receiver_request.status_code == 200:
        receiver_health = "Running"
    else:
        receiver_health = "Down"

    if storage_request.status_code == 200:
        storage_health = "Running"
    else:
        storage_health = "Down"

    if processing_request.status_code == 200:
        processing_health = "Running"
    else:
        processing_health = "Down"
    
    if audit_request.status_code == 200:
        audit_health = "Running"
    else:
        audit_health = "Down"

    stats = Check(receiver_health, storage_health, processing_health, audit_health, current_date)

    session.add(stats)
    session.commit()
    session.close()
    logger.info("Service health checks have been added")
    

def return_health_checks():
    """ Returns health checks """
    logger.info("Return health checks started")
    session = DB_SESSION()
    all_data = session.query(Check).order_by(Check.last_updated)
    print(all_data)
    last_updated = session.query(Check).order_by(Check.last_updated.desc()).first()
    if last_updated == None:
        logger.error("Health checks do not exist!")
    data_dict = last_updated.to_dict()
    logger.info("Return health checks has completed!")
    session.close()

    return data_dict, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(get_health_checks,'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()


def create_db():
    """ Creates sqlite database for when it doesn't exist """
    conn = sqlite3.connect(app_config['datastore']['filename'])
    c = conn.cursor()
    c.execute('''
        CREATE TABLE checks
        (id VARCHAR(100) PRIMARY KEY ASC,
        receiver VARCHAR(100) NOT NULL,
        storage VARCHAR(100) NOT NULL,
        processing VARCHAR(100) NOT NULL,
        audit VARCHAR(100) NOT NULL,
        last_updated VARCHAR(100) NOT NULL)
        ''')
    conn.commit()
    conn.close() 


logger.info(f"THE PATH IS {app_config['datastore']['filename']}")
if os.path.exists(app_config['datastore']['filename']) != True:
    create_db()
    logger.info(f"Created sqlite database!")

DB_ENGINE = create_engine(f"sqlite:///{app_config['datastore']['filename']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/health_check",strict_validation=False, validate_responses=True)

if __name__== "__main__":
    init_scheduler()
    app.run(port=8120, debug=True)