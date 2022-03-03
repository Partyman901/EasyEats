from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class Delivery(Base):
    """ Delivery """

    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True)
    address = Column(String(250), nullable=False)
    driver = Column(String(250), nullable=False)
    distance = Column(Integer, nullable=False)
    orderNum = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    traceID = Column(String(100), nullable=False)

    def __init__(self, address, driver, distance, orderNum, traceID):
        """ Initializes a delivery """
        self.address = address
        self.driver = driver
        self.distance = distance
        self.orderNum = orderNum
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.traceID = traceID

    def to_dict():
        """ Dictionary of the data """
        
    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['address'] = self.address
        dict['driver'] = self.driver
        dict['distance'] = self.distance
        dict['orderNum'] = self.orderNum
        dict['date_created'] = self.date_created
        dict['traceID'] = self.traceID

        return dict