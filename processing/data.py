from sqlalchemy import Column, Integer, String, DateTime
from base import Base

class Data(Base):
    """ Processing Statistics """
    __tablename__ = "enterdata"

    id = Column(Integer, primary_key=True)
    windows_vote = Column(Integer,nullable=True)
    mac_vote = Column(Integer, nullable=True)

    def __init__(self, windows_vote, mac_vote):
        """ Initializes a processing statistics objet """
        self.windows_vote = windows_vote
        self.mac_vote = mac_vote

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['windows_vote'] = self.windows_vote
        dict['mac_vote'] = self.mac_vote

        return dict