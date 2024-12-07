from app import db

class NPC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    alignment = db.Column(db.String(50))
    stats = db.Column(db.JSON)  # Store stats like STR, DEX, etc., as JSON
    abilities = db.Column(db.Text)  # Store special abilities
    spells = db.Column(db.Text)  # Store spell details
    racial_features = db.Column(db.Text)  # Store racial features
    description = db.Column(db.Text)  # Additional description or notes

    def to_dict(self):
        return {
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
