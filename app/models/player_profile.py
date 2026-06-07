"""
PlayerProfile model
-------------------
Stores a D&D 5e player character sheet.

Fields map 1-to-1 with the SRD 5e character sheet structure so the
data can later be used to auto-fill a PDF form (e.g. the WotC sheet).

Stats & proficiencies are stored as plain integers / text columns
rather than JSON to make them directly queryable and sortable.
"""

from app import db


class PlayerProfile(db.Model):
    __tablename__ = "player_profiles"

    # ── Identity ──────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    subspecies = db.Column(db.String(50), nullable=True)
    character_class = db.Column(db.String(50), nullable=False)
    background = db.Column(db.String(100), nullable=True)
    alignment = db.Column(db.String(50), nullable=True)

    # ── Ability Scores ────────────────────────────────────────────────────
    strength = db.Column(db.Integer, nullable=False, default=10)
    dexterity = db.Column(db.Integer, nullable=False, default=10)
    constitution = db.Column(db.Integer, nullable=False, default=10)
    intelligence = db.Column(db.Integer, nullable=False, default=10)
    wisdom = db.Column(db.Integer, nullable=False, default=10)
    charisma = db.Column(db.Integer, nullable=False, default=10)

    # ── Proficiencies ─────────────────────────────────────────────────────
    skills = db.Column(db.Text, nullable=True)
    tool_proficiencies = db.Column(db.Text, nullable=True)
    languages = db.Column(db.Text, nullable=True)
    saving_throws = db.Column(db.Text, nullable=True)

    # ── Combat Stats ──────────────────────────────────────────────────────
    hit_points = db.Column(db.Integer, nullable=False, default=10)
    armor_class = db.Column(db.Integer, nullable=False, default=10)
    speed = db.Column(db.Integer, nullable=False, default=30)
    initiative = db.Column(db.Integer, nullable=False, default=0)

    # ── Inventory & Equipment ─────────────────────────────────────────────
    equipment = db.Column(db.Text, nullable=True)
    weapons = db.Column(db.Text, nullable=True)
    spells = db.Column(db.Text, nullable=True)

    # ── Narrative ─────────────────────────────────────────────────────────
    description = db.Column(db.Text, nullable=True)
    backstory = db.Column(db.Text, nullable=True)

    # ── Campaign Relationship ─────────────────────────────────────────────
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("campaign_logs.id"), nullable=True
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "subspecies": self.subspecies,
            "character_class": self.character_class,
            "background": self.background,
            "alignment": self.alignment,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "skills": self.skills,
            "tool_proficiencies": self.tool_proficiencies,
            "languages": self.languages,
            "hit_points": self.hit_points,
            "armor_class": self.armor_class,
            "speed": self.speed,
            "initiative": self.initiative,
            "saving_throws": self.saving_throws,
            "equipment": self.equipment,
            "weapons": self.weapons,
            "spells": self.spells,
            "description": self.description,
            "backstory": self.backstory,
            "campaign_id": self.campaign_id,
        }
