"""
Campaign Routes  (/campaigns)
------------------------------
Read-only view of campaign logs for the frontend.
Campaign logs are primarily populated via the debug seed route
or direct DB tooling; editing is a planned future feature.
"""

from flask import Blueprint, jsonify

from app import db
from app.models.campaign import CampaignLog

campaign_bp = Blueprint("campaign", __name__, url_prefix="/campaigns")


@campaign_bp.route("", methods=["GET"])
def get_all_campaigns():
    """Return all campaign logs."""
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


@campaign_bp.route("/<int:log_id>", methods=["GET"])
def get_campaign(log_id: int):
    """Return a single campaign log."""
    log = db.get_or_404(CampaignLog, log_id)
    return jsonify({
        "id": log.id,
        "narrative": log.narrative,
        "encounters": log.encounters,
        "npc_details": log.npc_details,
    })
