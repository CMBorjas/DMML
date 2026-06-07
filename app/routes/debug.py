"""
Debug Routes  (/debug)
-----------------------
Development-only helpers for inspecting and seeding the database.
These routes are ONLY registered when the app runs in debug mode
(FLASK_DEBUG=1 or app.debug=True).

WARNING: Never deploy with FLASK_DEBUG=1 in production.
"""

from flask import Blueprint, jsonify

from app import db
from app.models.campaign import CampaignLog

debug_bp = Blueprint("debug", __name__, url_prefix="/debug")


@debug_bp.route("/campaign_logs", methods=["GET"])
def list_campaign_logs():
    """Return all campaign logs for inspection."""
    logs = CampaignLog.query.all()
    return jsonify([
        {
            "id": log.id,
            "narrative": log.narrative,
            "encounters": log.encounters,
            "npc_details": log.npc_details,
        }
        for log in logs
    ])


@debug_bp.route("/seed_campaign_logs", methods=["POST"])
def seed_campaign_logs():
    """Seed the database with example campaign logs (idempotent)."""
    if CampaignLog.query.count() > 0:
        return jsonify({"message": "Campaign logs already exist — skipping seed."}), 200

    example_logs = [
        {
            "narrative": "The party entered the haunted forest seeking the lost artifact.",
            "encounters": "They were ambushed by a pack of wolves and a band of goblins.",
            "npc_details": "They met a mysterious ranger named Kaelen who offered to guide them.",
        },
        {
            "narrative": "The party reached the ancient ruins and found the artifact.",
            "encounters": "They had to solve a magical puzzle to unlock the door.",
            "npc_details": "An old historian named Elenna shared knowledge about the artifact.",
        },
    ]

    for entry in example_logs:
        db.session.add(CampaignLog(**entry))

    db.session.commit()
    return jsonify({"message": "Campaign logs seeded successfully."}), 201
