"""
NPC model
---------
Represents a non-player character with a full D&D 5e character sheet.
Sheet data is stored as JSON so the schema is flexible without new migrations.
Chat history lives in the ChatMessage table (one-to-many).
"""

import random
from app import db
from app.models.dnd_data import generate_full_npc, CLASSES

# ---------------------------------------------------------------------------
# Name pool (flavour — role comes from the generated sheet)
# ---------------------------------------------------------------------------

_NAMES = [
    "Dora Toreral", "Flarin Dusk", "Eryn Leafwalker", "Kaelen Ashveil",
    "Mira Stoneheart", "Brennan the Grey", "Thessaly Vex", "Orin Coldwater",
    "Lirien Dawnwhisper", "Gorrak Ironfist", "Selene Duskmantle", "Thorn Ashwood",
    "Varis Nightveil", "Petra Goldwick", "Aldric Stonemark", "Zara Windchaser",
    "Fenwick Holloway", "Isolde Morrow", "Cael Brightmane", "Nyx Shadowthorn",
]


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class NPC(db.Model):
    __tablename__ = "npc"

    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False)
    role  = db.Column(db.String(50),  nullable=False)   # class name

    # Full character sheet stored as JSON
    sheet = db.Column(db.JSON, nullable=True, default=dict)

    # Legacy convenience columns (kept for API compat, derived from sheet)
    alignment       = db.Column(db.String(50))
    stats           = db.Column(db.JSON)
    abilities       = db.Column(db.Text)
    spells          = db.Column(db.Text)
    racial_features = db.Column(db.Text)
    description     = db.Column(db.Text)

    # One-to-many: structured chat history
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
        """Create a fully-formed NPC from the D&D 5e SRD tables."""
        name  = random.choice(_NAMES)
        sheet = generate_full_npc()
        sheet["CharacterName"] = name

        # Derive the role label from the CLASS_LEVEL field
        role = sheet["CLASS_LEVEL"].split()[0]

        # Build flattened legacy fields for API convenience
        spells_list = sheet.get("spells", [])
        class_data  = CLASSES.get(role, {})

        return cls(
            name=name,
            role=role,
            sheet=sheet,
            alignment=sheet["ALIGNMENT"],
            stats={
                "STR": sheet["STR"], "DEX": sheet["DEX"], "CON": sheet["CON"],
                "INT": sheet["INT"], "WIS": sheet["WIS"], "CHA": sheet["CHA"],
            },
            abilities=sheet.get("class_features", ""),
            spells=", ".join(spells_list) if spells_list else "None",
            racial_features=sheet.get("racial_features", ""),
            description=sheet.get("PersonalityTraits", ""),
        )

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------

    def to_dict(self, include_messages: bool = False) -> dict:
        data = {
            "id":             self.id,
            "name":           self.name,
            "role":           self.role,
            "alignment":      self.alignment,
            "stats":          self.stats,
            "abilities":      self.abilities,
            "spells":         self.spells,
            "racial_features":self.racial_features,
            "description":    self.description,
            # Full sheet (used by the expanded card UI)
            "sheet":          self.sheet or {},
        }
        if include_messages:
            data["messages"] = [
                m.to_dict() for m in self.messages.order_by("created_at")
            ]
        return data
