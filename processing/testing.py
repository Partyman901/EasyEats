from sqlalchemy.orm import sessionmaker
from base import Base
from sqlalchemy import create_engine
import yaml
from stats import Stats
from datetime import datetime

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

DB_ENGINE = create_engine("sqlite:///%s" % (app_config["datastore"]["filename"]))
Base.metadata.bind = DB_ENGINE 
DB_SESSION = sessionmaker(bind=DB_ENGINE)

session = DB_SESSION()
print(datetime.now())
readings = session.query(Stats).order_by(Stats.last_updated.desc()).all()

# results_list = [] 

# for reading in readings: 
#     results_list.append(reading.to_dict()) 

print(readings)
session.close() 