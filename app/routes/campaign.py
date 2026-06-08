"""
Campaign Routes  (/campaigns)
------------------------------
Read-only view of campaign logs for the frontend.
Campaign logs are primarily populated via the debug seed route
or direct DB tooling; editing is a planned future feature.
"""

from flask import Blueprint, jsonify, request

from app import db
from app.models.campaign import CampaignLog

campaign_bp = Blueprint("campaign", __name__, url_prefix="/campaigns")


def _validate_json(*required_fields: str):
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Request body must be valid JSON"}), 400)
    for field in required_fields:
        if field not in data:
            return None, (jsonify({"error": f"Missing required field: '{field}'"}), 400)
    return data, None


@campaign_bp.route("", methods=["GET"])
def get_all_campaigns():
    """Return all campaign logs."""
    logs = CampaignLog.query.order_by(CampaignLog.id.desc()).all()
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


@campaign_bp.route("", methods=["POST"])
def create_campaign():
    """Create a new campaign log."""
    data, err = _validate_json("narrative")
    if err:
        return err

    log = CampaignLog(
        narrative=data["narrative"],
        encounters=data.get("encounters"),
        npc_details=data.get("npc_details"),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({
        "id": log.id,
        "narrative": log.narrative,
        "encounters": log.encounters,
        "npc_details": log.npc_details,
    }), 201


@campaign_bp.route("/<int:log_id>", methods=["PUT"])
def update_campaign(log_id: int):
    """Update a campaign log."""
    data, err = _validate_json()
    if err:
        return err

    log = db.get_or_404(CampaignLog, log_id)
    log.narrative = data.get("narrative", log.narrative)
    log.encounters = data.get("encounters", log.encounters)
    log.npc_details = data.get("npc_details", log.npc_details)
    db.session.commit()
    return jsonify({
        "id": log.id,
        "narrative": log.narrative,
        "encounters": log.encounters,
        "npc_details": log.npc_details,
    })


@campaign_bp.route("/<int:log_id>", methods=["DELETE"])
def delete_campaign(log_id: int):
    """Delete a campaign log."""
    log = db.get_or_404(CampaignLog, log_id)
    db.session.delete(log)
    db.session.commit()
    return "", 204
