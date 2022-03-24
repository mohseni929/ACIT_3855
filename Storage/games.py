from ast import Str
import string
from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Games(Base):
    """games """

    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    Time = Column(String, nullable=False)
    Stadium = Column(String, nullable=False)
    Number_of_referees = Column(Integer, nullable=False)
    Level = Column(String, nullable=False)
    Capacity = Column(Integer, nullable=False)
    trace_id = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)
    

    def __init__(self, Time, Stadium, Number_of_referees, Level, Capacity, trace_id):
        """ Initializes a heart rate reading """
        self.Time = Time
        self.Stadium = Stadium
        self.Number_of_referees = Number_of_referees
        self.Level = Level
        self.Capacity = Capacity
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now().replace(microsecond=0) # Sets the date/time record is created
    
    def to_dict(self):
        """ Dictionary Representation of a heart rate reading """
        dict = {}
        dict['id'] = self.id
        dict['Time'] = self.Time
        dict['Stadium'] = self.Stadium
        dict['Number_of_referees'] = self.Number_of_referees
        dict['Level'] = self.Level
        dict['Capacity'] = self.Capacity
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created


        return dict
