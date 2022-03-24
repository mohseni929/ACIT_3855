from sqlalchemy import Column, Integer, String, DateTime, null
from base import Base
import datetime


class AvailableGames(Base):
    """ Blood Pressure """

    __tablename__ = "available_games"

    id = Column(Integer, primary_key=True)
    Game_id = Column(String, nullable=False)
    Location = Column(String, nullable=False)
    Teams = Column(String, nullable=False)
    Classification = Column(Integer, nullable=False)
    Referee_team = Column(String, nullable=False)
    trace_id = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)

    

    def __init__(self, Game_id, Location, Teams, Classification, Referee_team, trace_id):
        """ Initializes a blood pressure reading """
        self.Game_id = Game_id
        self.Location = Location
        self.Teams = Teams
        self.Classification = Classification
        self.Referee_team = Referee_team
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now().replace(microsecond=0) # Sets the date/time record is created
        
    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['Game_id'] = self.Game_id
        dict['Location'] = self.Location
        dict['Teams'] = self.Teams
        dict['Classification'] = self.Classification
        dict['Referee_team'] = self.Referee_team
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created
        return dict
