from sqlalchemy import Column, Integer, String, DateTime
from base import Base 
class Stats(Base): 
    """ Processing Statistics """ 
 
    __tablename__ = "stats" 
 
    id = Column(Integer, primary_key=True) 
    num_of_referees = Column(Integer, nullable=False) 
    num_of_experience = Column(Integer, nullable=False) 
    num_of_fans = Column(Integer, nullable=True) 
    num_of_fields = Column(Integer, nullable=True) 
    num_of_class = Column(Integer, nullable=True) 
    last_updated = Column(DateTime, nullable=False) 
 
    def __init__(self, num_of_referees, num_of_experience, num_of_fans, num_of_fields, num_of_class, last_updated): 
        """ Initializes a processing statistics object """ 
        self.num_of_referees = num_of_referees
        self.num_of_experience = num_of_experience 
        self.num_of_fans = num_of_fans 
        self.num_of_fields = num_of_fields 
        self.num_of_class = num_of_class 
        self.last_updated = last_updated 
 
    def to_dict(self): 
        """ Dictionary Representation of a statistics """ 
        dict = {} 
        dict['num_of_referees'] = self.num_of_referees 
        dict['num_of_experience'] = self.num_of_experience 
        dict['num_of_fans'] = self.num_of_fans 
        dict['num_of_fields'] = self.num_of_fields 
        dict['num_of_class'] = self.num_of_class 
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%d %H:%M:%S") 
 
        return dict