import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml
import logging.config
import uuid
import datetime
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import json
from base import Base
from flask_cors import CORS, cross_origin

# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger("audit")

# with open('app_conf.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())

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
logger = logging.getLogger('audit')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

user = app_config.get("datastore")["user"]
password = app_config.get("datastore")["password"]
hostname = app_config.get("datastore")["hostname"]
port = app_config.get("datastore")["port"]
db = app_config.get("datastore")["db"]

DB_ENGINE = create_engine(
    'mysql+pymysql://{}:{}@{}:{}/{}'.format(user, password, hostname, port, db))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def searchClassification(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],   
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
    
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
                                         consumer_timeout_ms=1000) 
    
    logger.info("Retrieving referee classification at index %d" % index) 
    current_index = 1
    try: 
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            current_index += 1
            if current_index == index:
                return msg, 200
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find referee available at index %d" % index) 
    return { "message": "Not Found"}, 404

def searchFans(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving number of fans at index %d" % index) 
    current_index = 1
    try: 
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            current_index += 1
            if current_index == index:
                return msg, 200
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find game at index %d" % index) 
    return { "message": "Not Found"}, 404

def searchExperience(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving referee experience at index %d" % index) 
    current_index = 1
    try: 
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            current_index += 1
            if current_index == index:
                return msg, 200
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find available stadium at index %d" % index) 
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='./')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)