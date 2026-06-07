"""
NPC model
---------
Represents a non-player character in the campaign.
Chat history is stored in the ChatMessage table (one-to-many)
rather than as a raw text blob.
"""

import random
from app import db

# ---------------------------------------------------------------------------
# Curated random pools for NPC generation
# (AI is only involved during live chat, not initial stat generation)
# ---------------------------------------------------------------------------

_NAMES = [
    "Dora Toreral", "Flarin Dusk", "Eryn Leafwalker", "Kaelen Ashveil",
    "Mira Stoneheart", "Brennan the Grey", "Thessaly Vex", "Orin Coldwater",
    "Lirien Dawnwhisper", "Gorrak Ironfist",
]

_ROLES = ["Minstrel", "Warrior", "Sorcerer", "Merchant", "Scholar",
          "Innkeeper", "Ranger", "Alchemist", "Spy", "Priest"]

_ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil",
]

_ABILITIES_BY_ROLE = {
    "Warrior":   ["Power Attack", "Shield Wall", "Rallying Cry"],
    "Sorcerer":  ["Arcane Surge", "Mana Shield", "Spell Echo"],
    "Ranger":    ["Hunter's Mark", "Evasion", "Animal Companion"],
    "Minstrel":  ["Bardic Inspiration", "Song of Rest", "Vicious Mockery"],
    "Priest":    ["Divine Smite", "Turn Undead", "Healing Word"],
    "default":   ["Keen Senses", "Quick Reflexes", "Resourceful"],
}

_SPELLS_BY_ROLE = {
    "Sorcerer": ["Fireball", "Counterspell", "Misty Step", "Charm Person"],
    "Priest":   ["Cure Wounds", "Sacred Flame", "Bless", "Guiding Bolt"],
    "Minstrel": ["Dissonant Whispers", "Faerie Fire", "Suggestion"],
    "default":  [],
}

_RACIAL_FEATURES = [
    "Darkvision (60 ft)",
    "Fey Ancestry — advantage on saving throws against being charmed",
    "Stonecunning — double proficiency bonus on History checks related to stonework",
    "Lucky — reroll 1s on attack rolls, ability checks, and saving throws",
    "Draconic Ancestry — breath weapon (fire, 15 ft cone, DC 13 DEX)",
    "Hellish Resistance — resistance to fire damage",
    "Gnome Cunning — advantage on INT/WIS/CHA saving throws against magic",
    "Relentless Endurance — drop to 1 HP instead of 0 once per long rest",
    "None",
]

_DESCRIPTIONS = [
    "A weathered traveller with a sharp eye and sharper tongue.",
    "Speaks little but observes everything; locals whisper of a troubled past.",
    "Cheerful on the surface, but something haunted lingers behind their smile.",
    "Commands respect through deeds, not words.",
    "Carries a battered journal filled with strange diagrams and cryptic notes.",
]


def _random_ability(role: str) -> str:
    pool = _ABILITIES_BY_ROLE.get(role, _ABILITIES_BY_ROLE["default"])
    return random.choice(pool)


def _random_spells(role: str) -> str:
    pool = _SPELLS_BY_ROLE.get(role, _SPELLS_BY_ROLE["default"])
    if not pool:
        return "None"
    return ", ".join(random.sample(pool, min(2, len(pool))))


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class NPC(db.Model):
    __tablename__ = "npc"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    alignment = db.Column(db.String(50))
    stats = db.Column(db.JSON)
    abilities = db.Column(db.Text)
    spells = db.Column(db.Text)
    racial_features = db.Column(db.Text)
    description = db.Column(db.Text)

    # Relationship to structured chat history
    messages = db.relationship(
        "ChatMessage",
        backref="npc",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # -----------------------------------------------------------------------
    # Factory
    # -----------------------------------------------------------------------

    @classmethod
    def generate_random(cls) -> "NPC":
        """Create a new NPC with randomised stats from curated pools."""
        role = random.choice(_ROLES)
        return cls(
            name=random.choice(_NAMES),
            role=role,
            alignment=random.choice(_ALIGNMENTS),
            stats={
                "STR": random.randint(8, 18),
                "DEX": random.randint(8, 18),
                "CON": random.randint(8, 18),
                "INT": random.randint(8, 18),
                "WIS": random.randint(8, 18),
                "CHA": random.randint(8, 18),
            },
            abilities=_random_ability(role),
            spells=_random_spells(role),
            racial_features=random.choice(_RACIAL_FEATURES),
            description=random.choice(_DESCRIPTIONS),
        )

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------

    def to_dict(self, include_messages: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "alignment": self.alignment,
            "stats": self.stats,
            "abilities": self.abilities,
            "spells": self.spells,
            "racial_features": self.racial_features,
            "description": self.description,
        }
        if include_messages:
            data["messages"] = [m.to_dict() for m in self.messages.order_by("created_at")]
        return data
