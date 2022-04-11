from logging.handlers import BufferingHandler
import connexion
import requests
import yaml
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from base import Base
from sqlalchemy import create_engine
from flask_cors import CORS, cross_origin
from sqlalchemy.orm import sessionmaker
from stats import Stats
from datetime import datetime
from uuid import uuid1
import os
from create_tables import create_database

#Configurable Variables
max_events = 10
yaml_file = "./openapi.yaml"

#System Variables

# with open('app_conf.yml', 'r') as f: 
#     app_config = yaml.safe_load(f.read())

# with open('log_conf.yml', 'r') as f: 
#     log_config = yaml.safe_load(f.read()) 
#     logging.config.dictConfig(log_config) 
# logger = logging.getLogger('basicLogger')

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
logger = logging.getLogger('audit')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

create_database()

def get_health():
    return 200

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"]) 
Base.metadata.bind = DB_ENGINE 
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    logger.info("Request has started.")

    session = DB_SESSION() 

    try:
        readings = session.query(Stats).order_by(Stats.last_updated.desc()).first()

        results = readings.to_dict()
    except:
        logger.error("Statistics do not exist.")
        results = {'num_of_referees': 0, 'num_of_experience': 0, 'num_of_fans': 0, 'num_of_fields': 0, 'num_of_class': 0, 'last_updated': '0001-01-01 01:01:01'}

    session.close()

    logger.debug(f"Python Dictionary Contents: {results}.")
    logger.info(f"Request has completed.")

    return results, 200

def populate_stats(): 
    """ Periodically update stats """ 
    logger.info(f"Periodic Request Process Has Started")

    session = DB_SESSION() 
 
    try:
        readings = session.query(Stats).order_by(Stats.last_updated.desc()).first()

        results = readings.to_dict()

        # for reading in readings: 
        #     results.append(reading.to_dict()) 
    except:
        results = {'num_of_referees': 0, 'num_of_experience': 0, 'num_of_fans': 0, 'num_of_fields': 0, 'num_of_class': 0, 'last_updated': '0001-01-01 01:01:01'}
    
    
    response1 = requests.get(f"{app_config['eventstore']['url']}/availability/schedule",params={'start_timestamp': results['last_updated'],'end_timestamp':datetime.now()})
    response2 = requests.get(f"{app_config['eventstore']['url']}/availability/game",params={'start_timestamp': results['last_updated'],'end_timestamp':datetime.now()})
    response3 = requests.get(f"{app_config['eventstore']['url']}/availability/referee",params={'start_timestamp': results['last_updated'],'end_timestamp':datetime.now()})

    print(f'\n\n{response1,response2,response3}\n\n')

    classes = response1.json()
    refs = response2.json()
    exp = response3.json()
    
    responses = len(classes) + len(refs) + len(exp)
    if classes != 0 and refs !=0 and exp !=0:
        if response1.ok and response2.ok and response3:
            logger.info(f"Total responses received: {responses}")
        else:
            logger.error("GET request failed.")

        trace_id = str(uuid1())


        total_fields = len(exp)
        total_referees = sum([x['Number_of_referees'] for x in refs]) + int(results["num_of_referees"])
        total_exp = sum([x['Experience'] for x in exp]) + int(results["num_of_experience"])
        total_capacity = sum([x['Capacity'] for x in refs]) + int(results["num_of_fans"])
        total_class = sum([x['Classification'] for x in classes]) + int(results["num_of_class"])

        logger.debug(f"Total number of fields and games: {total_fields}. TraceID: {trace_id}")
        logger.debug(f"Total number of referees {total_referees}. TraceID: {trace_id}")
        logger.debug(f"Total number of experience {total_exp}. TraceID: {trace_id}")
        logger.debug(f"Total number of fans {total_capacity}. TraceID: {trace_id}")
        logger.debug(f"Total number of classes {total_class}. TraceID: {trace_id}")

        current_time = datetime.now()

        stats = Stats(total_fields, 
                total_referees, 
                total_exp, 
                total_capacity, 
                total_class, 
                datetime.now().replace(microsecond=0))

        session.add(stats) 
    
        logger.debug(f"New Stat entry. TraceID: {trace_id}")

        session.commit()
    session.close()

    logger.info(f"Periodic Request Process has ended.")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True) 
    sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec']) 
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='Swagger/')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api(yaml_file, base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler() 
    app.run(port=8100, use_reloader=False)