import sqlite3 

def create_database():
    conn = sqlite3.connect('/data/data.sqlite')
    c = conn.cursor() 
    c.execute(''' 
            CREATE TABLE stats 
            (id INTEGER PRIMARY KEY ASC,  
            num_of_referees INTEGER NOT NULL, 
            num_of_experience INTEGER NOT NULL, 
            num_of_fans INTEGER, 
            num_of_fields INTEGER, 
            num_of_class INTEGER, 
            last_updated VARCHAR(100) NOT NULL) 
            ''') 
    
    conn.commit() 
    conn.close()
    print("table created")