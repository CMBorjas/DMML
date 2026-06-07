"""
ChatMessage model
-----------------
Stores individual NPC chat turns as structured rows instead of
appending raw text to a single column. This enables:
  - Pagination / lazy loading of long conversations
  - Per-message timestamps for session review
  - Clean serialisation to JSON for the frontend

Schema is intentionally compact — sender is a single char ('P' = player, 'N' = NPC)
to keep storage small on a laptop SQLite instance.
"""

from datetime import datetime, timezone
from app import db


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    npc_id = db.Column(db.Integer, db.ForeignKey("npc.id", ondelete="CASCADE"), nullable=False, index=True)
    # 'P' = player, 'N' = npc
    sender = db.Column(db.String(1), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "npc_id": self.npc_id,
            "sender": "player" if self.sender == "P" else "npc",
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }
