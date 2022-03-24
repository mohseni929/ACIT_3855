import mysql.connector 
 
db_conn = mysql.connector.connect(host="acit3855lab.westus.cloudapp.azure.com", user="user", 
password="password", database="events") 
 
db_cursor = db_conn.cursor() 
 
db_cursor.execute(''' 
          CREATE TABLE available_games
          (id INTEGER NOT NULL AUTO_INCREMENT, 
           Game_id VARCHAR(500) NOT NULL,
           Location VARCHAR(500) NOT NULL,
           Teams VARCHAR(500) NOT NULL,
           Classification INTEGER NOT NULL,
           Referee_team VARCHAR(500) NOT NULL,
           trace_id VARCHAR(500) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT available_pk PRIMARY KEY (id))
          ''')
 
db_cursor.execute(''' 
          CREATE TABLE games
          (id INTEGER NOT NULL AUTO_INCREMENT, 
           Time VARCHAR(500) NOT NULL,
           Stadium VARCHAR(500) NOT NULL,
           Number_of_referees INTEGER NOT NULL,
           Level VARCHAR(500) NOT NULL,
           Capacity INTEGER NOT NULL,
           trace_id VARCHAR(500) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT game_pk PRIMARY KEY (id))
          ''')

db_cursor.execute(''' 
          CREATE TABLE referee_available
          (id INTEGER AUTO_INCREMENT, 
           Referee_ID VARCHAR(500) NOT NULL,
           Name VARCHAR(500) NOT NULL,
           Age INTEGER NOT NULL,
           Classification INTEGER NOT NULL,
           address VARCHAR(500) NOT NULL,
           Phone_number VARCHAR(500) NOT NULL,
           Experience INTEGER NOT NULL,
           trace_id VARCHAR(500) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT ref_pk PRIMARY KEY (id))
          ''')
 
db_conn.commit() 
db_conn.close() 





