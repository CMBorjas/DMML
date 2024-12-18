from app import db

class NPC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    alignment = db.Column(db.String(50))
    stats = db.Column(db.JSON)
    abilities = db.Column(db.Text)
    spells = db.Column(db.Text)
    racial_features = db.Column(db.Text)
    description = db.Column(db.Text)
    chat_history = db.Column(db.Text, default="")  # Field to store chat history

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
            "chat_history": self.chat_history,  # Include chat history in the dict
        }
