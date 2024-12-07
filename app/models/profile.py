from sqlalchemy import Column, Integer, String, Text
from app import db

class PlayerProfile(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    background = Column(Text)
    inventory = Column(Text)
    stats = Column(Text)
    actions = Column(Text)
