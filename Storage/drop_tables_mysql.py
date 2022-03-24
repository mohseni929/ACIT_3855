import mysql.connector 
 
db_conn = mysql.connector.connect(host="acit3855lab.westus.cloudapp.azure.com", user="user", 
password="password", database="events") 
 
db_cursor = db_conn.cursor() 
 
db_cursor.execute(''' 
                  DROP TABLE available_games, games, referee_available 
                  ''') 
 
db_conn.commit() 
db_conn.close() 
 
 


# import sqlite3

# conn = sqlite3.connect('point.sqlite')

# c = conn.cursor()
# c.execute('''
#           DROP TABLE point
#           ''')

# conn.commit()
# conn.close()
