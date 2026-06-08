"""
NPC Routes  (/npc)
------------------
CRUD operations for NPCs plus AI-powered chat, quest, and loot generation.
"""

from flask import Blueprint, request, jsonify

from app import db
from app.models.npc import NPC
from app.models.chat_message import ChatMessage
from app.models.ai import generate_suggestion_with_context, generate_quest, generate_loot

npc_bp = Blueprint("npc", __name__, url_prefix="/npc")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_json(*required_fields: str):
    """Return (data, error_response) tuple. error_response is None on success."""
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Request body must be valid JSON"}), 400)
    for field in required_fields:
        if field not in data:
            return None, (jsonify({"error": f"Missing required field: '{field}'"}), 400)
    return data, None


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@npc_bp.route("", methods=["GET"])
def get_all_npcs():
    """Return all NPCs (without full message history)."""
    npcs = NPC.query.all()
    return jsonify([npc.to_dict() for npc in npcs])


@npc_bp.route("/<int:npc_id>", methods=["GET"])
def get_npc(npc_id: int):
    """Return a single NPC with its full chat message history."""
    npc = db.get_or_404(NPC, npc_id)
    return jsonify(npc.to_dict(include_messages=True))


@npc_bp.route("", methods=["POST"])
def create_npc():
    """Create a new NPC from a JSON payload."""
    data, err = _validate_json("name", "role")
    if err:
        return err

    npc = NPC(
        name=data["name"],
        role=data["role"],
        alignment=data.get("alignment", "True Neutral"),
        stats=data.get("stats", {}),
        abilities=data.get("abilities", ""),
        spells=data.get("spells", ""),
        racial_features=data.get("racial_features", ""),
        description=data.get("description", ""),
    )
    db.session.add(npc)
    db.session.commit()
    return jsonify(npc.to_dict()), 201


@npc_bp.route("/generate", methods=["POST"])
def generate_npc():
    """Generate and persist a random NPC using curated stat pools."""
    npc = NPC.generate_random()
    db.session.add(npc)
    db.session.commit()
    return jsonify(npc.to_dict()), 201


@npc_bp.route("/<int:npc_id>", methods=["PUT"])
def update_npc(npc_id: int):
    """Update fields on an existing NPC."""
    data, err = _validate_json()
    if err:
        return err

    npc = db.get_or_404(NPC, npc_id)
    npc.name = data.get("name", npc.name)
    npc.role = data.get("role", npc.role)
    npc.alignment = data.get("alignment", npc.alignment)
    npc.stats = data.get("stats", npc.stats)
    npc.abilities = data.get("abilities", npc.abilities)
    npc.spells = data.get("spells", npc.spells)
    npc.racial_features = data.get("racial_features", npc.racial_features)
    npc.description = data.get("description", npc.description)
    db.session.commit()
    return jsonify(npc.to_dict())


@npc_bp.route("/<int:npc_id>", methods=["DELETE"])
def delete_npc(npc_id: int):
    """Delete an NPC and all of its associated chat messages."""
    npc = db.get_or_404(NPC, npc_id)
    db.session.delete(npc)
    db.session.commit()
    return "", 204


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@npc_bp.route("/<int:npc_id>/chat", methods=["POST"])
def chat_with_npc(npc_id: int):
    """
    Send a player message to an NPC and receive an AI response.
    Stores both turns as structured ChatMessage rows.
    """
    data, err = _validate_json("input")
    if err:
        return err

    player_input = data["input"].strip()
    if not player_input:
        return jsonify({"error": "Input must not be empty"}), 400

    npc = db.get_or_404(NPC, npc_id)

    # Retrieve the last 5 turns for context (player + npc messages alternating)
    recent = (
        npc.messages.order_by(ChatMessage.created_at.desc()).limit(10).all()
    )
    recent.reverse()
    recent_text = [
        f"{'Player' if m.sender == 'P' else npc.name}: {m.content}"
        for m in recent
    ]

    # Generate AI response using the active provider
    response = generate_suggestion_with_context(
        query=player_input,
        npc_name=npc.name,
        recent_interactions=recent_text,
    )

    # Persist both turns
    db.session.add(ChatMessage(npc_id=npc.id, sender="P", content=player_input))
    db.session.add(ChatMessage(npc_id=npc.id, sender="N", content=response))
    db.session.commit()

    return jsonify({
        "npc_response": response,
        "messages": [m.to_dict() for m in npc.messages.order_by("created_at")],
    })


@npc_bp.route("/<int:npc_id>/chat_stream", methods=["POST"])
def chat_with_npc_stream(npc_id: int):
    """
    Stream AI response token-by-token.
    """
    data, err = _validate_json("input")
    if err:
        return err

    player_input = data["input"].strip()
    if not player_input:
        return jsonify({"error": "Input must not be empty"}), 400

    npc = db.get_or_404(NPC, npc_id)

    recent = npc.messages.order_by(ChatMessage.created_at.desc()).limit(10).all()
    recent.reverse()
    recent_text = [
        f"{'Player' if m.sender == 'P' else npc.name}: {m.content}"
        for m in recent
    ]

    # Persist player turn immediately
    db.session.add(ChatMessage(npc_id=npc.id, sender="P", content=player_input))
    db.session.commit()

    from flask import Response, stream_with_context, current_app
    from app.models.ai import generate_stream_with_context

    def generate():
        app = current_app._get_current_object()
        with app.app_context():
            full_response = ""
            for chunk in generate_stream_with_context(player_input, npc.name, recent_text):
                full_response += chunk
                yield chunk
            
            # Persist AI response
            db.session.add(ChatMessage(npc_id=npc.id, sender="N", content=full_response))
            db.session.commit()

    return Response(stream_with_context(generate()), mimetype='text/plain')


@npc_bp.route("/<int:npc_id>/chat", methods=["GET"])
def get_chat_history(npc_id: int):
    """Return the full chat history for a given NPC."""
    npc = db.get_or_404(NPC, npc_id)
    messages = npc.messages.order_by(ChatMessage.created_at).all()
    return jsonify([m.to_dict() for m in messages])


# ---------------------------------------------------------------------------
# AI Actions
# ---------------------------------------------------------------------------

@npc_bp.route("/<int:npc_id>/generate_quest", methods=["POST"])
def generate_quest_for_npc(npc_id: int):
    """Generate an AI quest request from the NPC and log it to chat history."""
    data, err = _validate_json()
    if err:
        return err

    npc = db.get_or_404(NPC, npc_id)
    location = (data or {}).get("location", "an unknown location")

    quest_text = generate_quest(npc.name, location)

    # Log the quest as an NPC chat message
    db.session.add(ChatMessage(npc_id=npc.id, sender="N", content=quest_text))
    db.session.commit()

    return jsonify({"quest": quest_text})


@npc_bp.route("/<int:npc_id>/generate_loot", methods=["POST"])
def generate_loot_for_npc(npc_id: int):
    """Generate AI loot rewards and log them to the NPC's chat history."""
    npc = db.get_or_404(NPC, npc_id)
    data = request.get_json(silent=True) or {}
    quest_name = data.get("quest_name", "the recent quest")

    loot_text = generate_loot(quest_name)

    db.session.add(ChatMessage(npc_id=npc.id, sender="N", content=loot_text))
    db.session.commit()

    return jsonify({"loot": loot_text})
