from sqlalchemy import Column, Integer, String, DateTime
from base import Base

class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_orders = Column(Integer, nullable=False)
    num_deliveries = Column(Integer, nullable=False)
    max_price_purchase = Column(Integer, nullable=True)
    max_distance_delivery = Column(Integer, nullable=True)
    avg_price_purchase = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_orders, num_deliveries, max_price_purchase, max_distance_delivery, avg_price_purchase, last_updated):
        """ Initializes a processing statistics objet """
        self.num_orders = num_orders
        self.num_deliveries = num_deliveries
        self.max_price_purchase = max_price_purchase
        self.max_distance_delivery = max_distance_delivery
        self.avg_price_purchase = avg_price_purchase
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_orders'] = self.num_orders
        dict['num_deliveries'] = self.num_deliveries
        dict['max_price_purchase'] = self.max_price_purchase
        dict['max_distance_delivery'] = self.max_distance_delivery
        dict['avg_price_purchase'] = self.max_price_purchase
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        return dict