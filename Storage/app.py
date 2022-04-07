import connexion
from connexion import NoContent
from platform import python_branch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from available_games import AvailableGames
from games import Games
from referee_available import RefereeAvailable
import yaml
import datetime
import logging.config
from pykafka import KafkaClient
import json
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
import time


with open('app_conf.yml', 'r') as f:
    app_conf = yaml.safe_load(f.read())
    user = app_conf['datastore']['user']
    password = app_conf['datastore']['password']
    hostname = app_conf['datastore']['hostname']
    port = app_conf['datastore']['port']
    db = app_conf['datastore']['db']

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    
host_name = "%s:%d" % (app_conf["events"]["hostname"], app_conf["events"]["port"])
max_retry = app_conf["events"]["retry"]
retry = 0
while retry < max_retry:
    logger.info(f"Try to connect Kafka Server, this is number {retry} try")
    try:
        client = KafkaClient(hosts=host_name)
        topic = client.topics[str.encode(app_conf["events"]["topic"])]
        logger.info("Successfully connect to Kafka")
        consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False,
                                            auto_offset_reset=OffsetType.LATEST)
        break
    except:
        logger.error(f"Failed to connect to Kafka, this is number {retry} try")
        time.sleep(app_conf["events"]["sleep"])
        retry += 1
        logger.info("retry in 10 second")



DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')
logger.info(f"Connecting to DB. Hostname:{hostname}, Port:{port}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)




def searchClassification(start_timestamp, end_timestamp):
    session = DB_SESSION()

    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
   
    readings = session.query(AvailableGames).filter(
        and_(AvailableGames.date_created >= start_timestamp,
             AvailableGames.date_created < end_timestamp))
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for referee classification after %s returns %d results" % (start_timestamp, end_timestamp, len(results_list))) 
    
    # logger.info(f"Connecting to DB. Hostname:{hostname}, Port:{port}")
    return results_list, 200



def searchFans(start_timestamp, end_timestamp):
    session = DB_SESSION()

    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
   
    readings = session.query(Games).filter(
        and_(Games.date_created >= start_timestamp,
             Games.date_created < end_timestamp))
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for number of fans after %s returns %d results" % (start_timestamp, end_timestamp, len(results_list))) 
    
    # logger.info(f"Connecting to DB. Hostname:{hostname}, Port:{port}")
    return results_list, 200


def searchExperience(start_timestamp, end_timestamp):
    session = DB_SESSION()

    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
   
    readings = session.query(RefereeAvailable).filter(
        and_(RefereeAvailable.date_created >= start_timestamp,
             RefereeAvailable.date_created < end_timestamp))
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for referee's experience level after %s returns %d results" % (start_timestamp, end_timestamp, len(results_list))) 
    
    # logger.info(f"Connecting to DB. Hostname:{hostname}, Port:{port}")
    return results_list, 200


def process_messages(): 
    """ Process event messages """ 
    hostname = "%s:%d" % (app_conf["events"]["hostname"],   
                          app_conf["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_conf["events"]["topic"])] 
     
    # Create a consume on a consumer group, that only reads new messages  
    # (uncommitted messages) when the service re-starts (i.e., it doesn't  
    # read all the old messages from the history in the message queue). 
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                         reset_offset_on_start=False, 
                                         auto_offset_reset=OffsetType.LATEST) 
 
    # This is blocking - it will wait for a new message 
    for msg in consumer: 
        msg_str = msg.value.decode('utf-8') 
        msg = json.loads(msg_str) 
        logger.info("Message: %s" % msg) 
        payload = msg["payload"] 
        
        session = DB_SESSION()
        data = {}
 
        if msg["type"] == "available_games": # Change this to your event ty

            data = AvailableGames(payload['Game_id'],
                            payload['Location'],
                            payload['Teams'],
                            payload['Classification'],
                            payload['Referee_team'],
                            payload['trace_id'])


        elif msg["type"] == "games":

            data = Games(payload['Time'],
                        payload['Stadium'],
                        payload['Number_of_referees'],
                        payload['Level'],
                        payload['Capacity'],
                        payload['trace_id'])

            
        elif msg["type"] == "referee_available": # Change this to your event type  

            data = RefereeAvailable(payload['Referee_ID'],
                        payload['Name'],
                        payload['Age'],
                        payload['Classification'],
                        payload['Address'],
                        payload['Phone_Number'],
                        payload['Experience'],
                        payload['trace_id'])

        session.add(data)
        session.commit()
        session.close()
        logger.debug(f'Stored event {msg["type"]} request with a trace id of {payload["trace_id"]}')
        consumer.commit_offsets()
        
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages) 
    t1.setDaemon(True) 
    t1.start()
    
    app.run(port=8090)
