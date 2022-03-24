from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class RefereeAvailable(Base):
    """ Heart Rate """

    __tablename__ = "referee_available"

    id = Column(Integer, primary_key=True)
    Referee_ID = Column(String, nullable=False)
    Name = Column(String, nullable=False)
    Age = Column(Integer, nullable=False)
    Classification = Column(Integer, nullable=False)
    Address = Column(String, nullable=False)
    Phone_Number = Column(String, nullable=False)
    Experience = Column(Integer, nullable=False)
    trace_id = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, Referee_ID, Name, Age, Classification, Address, Phone_Number, Experience, trace_id):
        """ Initializes a heart rate reading """
        self.Referee_ID = Referee_ID
        self.Name = Name
        self.Age = Age
        self.Classification = Classification
        self.date_created = datetime.datetime.now().replace(microsecond=0) # Sets the date/time record is created # Sets the date/time record is created
        self.Address = Address
        self.Phone_Number = Phone_Number
        self.trace_id = trace_id
        self.Experience = Experience

    def to_dict(self):
        """ Dictionary Representation of a heart rate reading """
        dict = {}
        dict['id'] = self.id
        dict['Referee_ID'] = self.Referee_ID
        dict['Name'] = self.Name
        dict['Age'] = self.Age
        dict['Classification'] = self.Classification
        dict['Address'] = self.Address
        dict['Phone_Number'] = self.Phone_Number
        dict['Experience'] = self.Experience
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
