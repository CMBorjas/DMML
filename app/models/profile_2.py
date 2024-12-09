from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app import db


class PlayerProfile(db.Model):
    __tablename__ = 'player_profile'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    race_id = Column(Integer, ForeignKey('race.id'))
    class_id = Column(Integer, ForeignKey('character_class.id'))
    background = Column(Text, nullable=True)
    alignment = Column(String(50), nullable=True)
    level = Column(Integer, default=1)

    # Attributes
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)

    # Relationships
    race = relationship('Race', back_populates='players')
    character_class = relationship('CharacterClass', back_populates='players')
    inventory = relationship('Equipment', back_populates='owner')
    spells = relationship('Spell', back_populates='caster')

    # Additional fields for skills and proficiencies
    skills = Column(Text, nullable=True)  # JSON or comma-separated list
    tool_proficiencies = Column(Text, nullable=True)

    # Spell slots and class-specific features
    spell_slots = Column(Text, nullable=True)  # JSON structure for spell slots tracking


class Race(db.Model):
    __tablename__ = 'race'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    attribute_bonuses = Column(Text, nullable=True)  # JSON or comma-separated list

    # Relationships
    players = relationship('PlayerProfile', back_populates='race')


class CharacterClass(db.Model):
    __tablename__ = 'character_class'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    hit_die = Column(Integer, nullable=True)  # e.g., 6 for Wizard, 12 for Barbarian
    features = Column(Text, nullable=True)  # JSON or comma-separated list

    # Relationships
    players = relationship('PlayerProfile', back_populates='character_class')


class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('player_profile.id'))

    # Relationships
    owner = relationship('PlayerProfile', back_populates='inventory')


class Spell(db.Model):
    __tablename__ = 'spell'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    caster_id = Column(Integer, ForeignKey('player_profile.id'))

    # Relationships
    caster = relationship('PlayerProfile', back_populates='spells')
