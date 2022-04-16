from email.policy import default
import connexion
import logging.config
import requests
import yaml
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS
from base import Base
from health import Health
import os
import os.path
from create_table import create_database


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
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('health')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)


def check_data():
    file_exists = os.path.exists(f'{app_config["datastore"]["filename"]}')
    if file_exists:
        logger.info(f'log path is {app_config["datastore"]["filename"]}')
        logger.info("health.sqlite is exist")
    else:
        logger.info("HEALTH.SQLITE IS NOT CREATED")
        create_database()
        logger.info("CREATE HEALTH.SQLITE")

 
DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_health():
    """ Gets service health """
    session = DB_SESSION()
    logger.info("Start Get Health request")
    try:
        health = session.query(Health).order_by(Health.last_updated.desc()).first()
        session.close()
        return health.to_dict(), 200
    except:
        return "Statistics do not exist", 404

def populate_health():
    """ Periodically update health """
    logger.info("Start Periodic Health")
    session = DB_SESSION()
    try:
        health = session.query(Health).order_by(Health.last_updated.desc()).first()
        health = health.to_dict()
    
    except:
        default= "Sorry, not working!"
        health = {
                "reciever": default,
                "storage": default,
                "processing": default,
                "audit_log": default,
                "last_updated": datetime.datetime.now()
            }

    for service in ['storage', 'reciever', 'processing', 'audit_log']:
        maxtime = app_config["response"]['period_sec']
        request_health = requests.get(f"http://acit3855lab.westus.cloudapp.azure.com/{service}/health", timeout=maxtime)
        if request_health.status_code != 200:
            logger.error(f'{service} not running ')
        else:
            logger.info(f'{service} running ')
            health[f'{service}'] = 'great (^.^)!'


    add_health = Health(
        health["reciever"],
        health["storage"],
        health["processing"],
        health["audit_log"],
        datetime.datetime.now()
    )
    session.add(add_health)
    session.commit()
    session.close()

    logger.debug(
        f'The new processed statistics is {health}')
    logger.info("Periodic Health Ends")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(check_data, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.add_job(populate_health, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yaml', base_path="/health", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)