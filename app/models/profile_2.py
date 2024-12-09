from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from app import db

class PlayerProfile(db.Model):
    # Id used to find the player in the database
    id = Column(Integer, primary_key=True)
    # Name of the character
    name = Column(String(100), nullable=False)
    # race_id and class_id are foreign keys to discriminate between
    race_id = Column(Integer, ForeignKey('race.id'))
    class_id = Column(Integer, ForeignKey('character_class.id'))
    # Background used for the character
    background = Column(Text, nullable=True)
    # Alignment of the character
    alignment = Column(String(50), nullable=True)
    # Level of the character
    level = Column(Integer, default=1)

    # Attributes Should be between 1 and 20
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)

    # Relationships for the tables
    race = relationship('Race', back_populates='players')
    character_class = relationship('CharacterClass', back_populates='players')
    inventory = relationship('Equipment', back_populates='owner')
    spells = relationship('Spell', back_populates='caster')

    # Skills and proficiencies (can be extended)
    skills = Column(Text)  # JSON or comma-separated list of skill proficiencies
    tool_proficiencies = Column(Text)  # JSON or comma-separated tools

    # Spell slots and class-specific features
    spell_slots = Column(Text)  # JSON structure for spell slots tracking

class Race(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    attribute_bonuses = Column(Text)  # JSON or comma-separated list of bonuses

    # Relationships
    players = relationship('PlayerProfile', back_populates='race')

class CharacterClass(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    hit_die = Column(Integer)  # e.g., 6 for Wizard, 12 for Barbarian
    features = Column(Text)  # JSON or comma-separated list of class features

    # Relationships
    players = relationship('PlayerProfile', back_populates='character_class')

class Equipment(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('player_profile.id'))

    # Relationships
    owner = relationship('PlayerProfile', back_populates='inventory')

class Spell(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer)
    description = Column(Text, nullable=True)
    caster_id = Column(Integer, ForeignKey('player_profile.id'))

    # Relationships
    caster = relationship('PlayerProfile', back_populates='spells')
