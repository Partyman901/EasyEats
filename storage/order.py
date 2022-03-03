from tokenize import Floatnumber
from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class Order(Base):
    """ Order """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer = Column(String(250), nullable=False)
    food = Column(String(250), nullable=False)
    orderID = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    traceID = Column(String(100), nullable=False)

    def __init__(self, customer, food, orderID, price, traceID):
        """ Initializes an order """
        self.customer = customer
        self.food = food
        self.orderID = orderID
        self.price = price
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.traceID = traceID

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['customer'] = self.customer
        dict['food'] = self.food
        dict['orderID'] = self.orderID
        dict['price'] = self.price
        dict['date_created'] = self.date_created
        dict['traceID'] = self.traceID

        return dict