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

#send = requests.post
header = {'Content-Type': 'application/json'}


def write_request_json(req_str):
    """add a attributes to json"""
    if os.path.isfile("events.json"): 
        with open("events.json" , "r+") as file:
            file_content = json.load(file)      # loads content as json to file
    else: 
        file_content = []

    new_object = {
        "received_timestamp": str(datetime.now()),
        "request_data": ["%s is %s" % (keys, req_str[keys]) for keys in req_str]
    }                                           # adds the timestamp and request into variable
    
    file_content.append(new_object)             # add the timestamp and request to json

    if len(file_content)> 10:                   # oldest requests after 10th gets removed
        file_content = file_content[1:]
    
    with open("events.json", "w+") as outfile:
        json_object = json.dumps(file_content, indent = 4)
        outfile.write(json_object)
    return

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    scheduler = app_config['eventstore1']['url']
    game = app_config['eventstore2']['url']
    referee = app_config['eventstore3']['url']
    client = KafkaClient(hosts='acit3855lab.westus.cloudapp.azure.com:9092') 
    topic = client.topics[str.encode(app_config['events']['topic'])] 
    producer = topic.get_sync_producer()

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config) 
    logger = logging.getLogger('basicLogger')
    logger.info("Test")

def available_games(body):
    """add a new available game """
    trace_id = str(uuid1())
    logger.info(f"Recieved event status with a trace id of {trace_id}")
    body["trace_id"] = trace_id
    # status_code = send (scheduler, json.dumps(body), headers=header)
    # logger.info(f"Returned event status response id: {trace_id} with status {status_code}")
    #requests.post(scheduler, json=body, headers={"Content-Type": "application/json"})
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
    # status_code = send (game, json.dumps(body), headers=header)
    # logger.info(f"Returned event status response id: {trace_id} with status {status_code}")
    #requests.post(game, json=body, headers={"Content-Type": "application/json"})
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
    # status_code = send (referee, json.dumps(body), headers=header)
    # logger.info(f"Returned event status response id: {trace_id} with status {status_code}")
    #requests.post(referee, json=body, headers={"Content-Type": "application/json"})
    msg = { "type": "referee_available",  
        "datetime" :    
           datetime.datetime.now().strftime( 
             "%Y-%m-%dT%H:%M:%S"),  
        "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8')) 
    return NoContent, 201




app = connexion.FlaskApp(__name__, specification_dir='',)    # Flask app to run the file
app.add_api("openapi.yml", strict_validation = True, validate_responses = True)   # Add the yml file with validation
 
if __name__ == "__main__":   # Run program
    app.run(port=8080, debug=True)







