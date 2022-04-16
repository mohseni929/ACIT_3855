from asyncio import events
import connexion
from connexion import NoContent
import json
from datetime import datetime
import os
import requests
import yaml
import logging.config
import datetime
from pykafka import KafkaClient
from uuid import uuid1 
import time

#send = requests.post
header = {'Content-Type': 'application/json'}



# with open('app_conf.yml', 'r') as f: 
#     app_config = yaml.safe_load(f.read())
#     scheduler = app_config['eventstore1']['url']
#     game = app_config['eventstore2']['url']
#     referee = app_config['eventstore3']['url']
#     # client = KafkaClient(hosts='acit3855lab.westus.cloudapp.azure.com:9092') 
#     # topic = client.topics[str.encode(app_config['events']['topic'])] 
#     # producer = topic.get_sync_producer()

# with open('log_conf.yml', 'r') as f: 
#     log_config = yaml.safe_load(f.read()) 
#     logging.config.dictConfig(log_config) 
#     logger = logging.getLogger('basicLogger')
#     logger.info("Test")

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
    scheduler = app_config['eventstore1']['url']
    game = app_config['eventstore2']['url']
    referee = app_config['eventstore3']['url']
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    logger.info("Test")
logger = logging.getLogger('audit')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)
    
host_name = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
max_retry = app_config["events"]["retry"]
retry = 0
while retry < max_retry:
    logger.info(f"Try to connect Kafka Server, this is number {retry} try")
    try:
        client = KafkaClient(hosts=host_name)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        logger.info(f"Successfully connected to Kafka Server")
        break
    except:
        logger.error(f"Failed to connect to Kafka, this is number {retry} try")
        time.sleep(app_config["events"]["sleep"])
        retry += 1
        logger.info("retry in 10 second")

def get_health():
    return NoContent, 200


def available_games(body):
    """add a new available game """
    trace_id = str(uuid1())
    logger.info(f"Recieved event status with a trace id of {trace_id}")
    body["trace_id"] = trace_id
    producer = topic.get_sync_producer()
    msg = { "type": "available_games",  
        "datetime" :    
           datetime.datetime.now().strftime( 
             "%Y-%m-%dT%H:%M:%S"),  
        "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8')) 
    return NoContent, 201

def games(body):
    """adds the information about the game"""
    trace_id = str(uuid1())
    logger.info(f"Recieved event status with a trace id of {trace_id}")
    body["trace_id"] = trace_id
    producer = topic.get_sync_producer()
    msg = { "type": "games",  
        "datetime" :    
           datetime.datetime.now().strftime( 
             "%Y-%m-%dT%H:%M:%S"),  
        "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8')) 
    return NoContent, 201

def referee_available(body):
    """Add referee info and availability"""
    trace_id = str(uuid1())
    logger.info(f"Recieved event status with a trace id of {trace_id}")
    body["trace_id"] = trace_id
    producer = topic.get_sync_producer()
    msg = { "type": "referee_available",  
        "datetime" :    
           datetime.datetime.now().strftime( 
             "%Y-%m-%dT%H:%M:%S"),  
        "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8')) 
    return NoContent, 201




app = connexion.FlaskApp(__name__, specification_dir='',)    # Flask app to run the file
app.add_api("openapi.yml", base_path="/reciever", strict_validation = True, validate_responses = True)   # Add the yml file with validation
 
if __name__ == "__main__":   # Run program
    app.run(port=8080, debug=True)







