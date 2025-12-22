from sqlalchemy import Column, Integer, String, Text
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    category = Column(String)
    location_lat = Column(String) # Latitude
    location_lng = Column(String) # Longitude
    status = Column(String, default="lost") # lost / found