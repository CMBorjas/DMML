"""
Player Profile Routes  (/player_profiles)
-----------------------------------------
Consolidated CRUD for player characters.
Single schema, single URL prefix — /player and /player_profile legacy
routes have been removed.
"""

from flask import Blueprint, request, jsonify, send_file
import os
import io
import fitz  # PyMuPDF

from app import db
from app.models.player_profile import PlayerProfile

player_bp = Blueprint("player", __name__, url_prefix="/player_profiles")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_json(*required_fields: str):
    """Return (data, error_response). error_response is None on success."""
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

@player_bp.route("", methods=["GET"])
def get_all_players():
    """Return all player profiles."""
    players = PlayerProfile.query.all()
    return jsonify([p.to_dict() for p in players])


@player_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id: int):
    """Return a single player profile."""
    player = db.get_or_404(PlayerProfile, player_id)
    return jsonify(player.to_dict())


@player_bp.route("", methods=["POST"])
def create_player():
    """
    Create a new player profile.

    Required fields: name, species, character_class
    Stats can be provided as a dict  { STR, DEX, CON, INT, WIS, CHA }
    or as individual fields (strength, dexterity, etc.).
    """
    data, err = _validate_json("name", "species", "character_class")
    if err:
        return err

    # Support both { stats: { STR: 15, ... } } and flat fields
    stats = data.get("stats", {})

    player = PlayerProfile(
        name=data["name"],
        species=data["species"],
        subspecies=data.get("subspecies", ""),
        character_class=data["character_class"],
        background=data.get("background", ""),
        alignment=data.get("alignment", "True Neutral"),
        strength=stats.get("STR", data.get("strength", 10)),
        dexterity=stats.get("DEX", data.get("dexterity", 10)),
        constitution=stats.get("CON", data.get("constitution", 10)),
        intelligence=stats.get("INT", data.get("intelligence", 10)),
        wisdom=stats.get("WIS", data.get("wisdom", 10)),
        charisma=stats.get("CHA", data.get("charisma", 10)),
        skills=data.get("skills", ""),
        tool_proficiencies=data.get("tool_proficiencies", ""),
        languages=data.get("languages", ""),
        hit_points=data.get("hit_points", 10),
        armor_class=data.get("armor_class", 10),
        speed=data.get("speed", 30),
        initiative=data.get("initiative", 0),
        saving_throws=data.get("saving_throws", ""),
        equipment=data.get("equipment", ""),
        weapons=data.get("weapons", ""),
        spells=data.get("spells", ""),
        description=data.get("description", ""),
        backstory=data.get("backstory", ""),
        campaign_id=data.get("campaign_id"),
    )
    db.session.add(player)
    db.session.commit()
    return jsonify(player.to_dict()), 201


@player_bp.route("/<int:player_id>", methods=["PUT"])
def update_player(player_id: int):
    """Update fields on an existing player profile."""
    data, err = _validate_json()
    if err:
        return err

    player = db.get_or_404(PlayerProfile, player_id)
    updatable = [
        "name", "species", "subspecies", "character_class", "background",
        "alignment", "strength", "dexterity", "constitution", "intelligence",
        "wisdom", "charisma", "skills", "tool_proficiencies", "languages",
        "hit_points", "armor_class", "speed", "initiative", "saving_throws",
        "equipment", "weapons", "spells", "description", "backstory",
    ]
    for field in updatable:
        if field in data:
            setattr(player, field, data[field])

    db.session.commit()
    return jsonify(player.to_dict())


@player_bp.route("/<int:player_id>", methods=["DELETE"])
def delete_player(player_id: int):
    """Delete a player profile."""
    player = db.get_or_404(PlayerProfile, player_id)
    db.session.delete(player)
    db.session.commit()
    return "", 204
@player_bp.route("/<int:player_id>/export_pdf", methods=["GET"])
def export_pdf(player_id: int):
    """Export a PlayerProfile to a fillable WotC D&D 5e Character Sheet PDF."""
    player = db.get_or_404(PlayerProfile, player_id)
    
    # Path to the empty template
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "Example", "Example_Character_sheet.pdf"
    )
    if not os.path.exists(template_path):
        return jsonify({"error": "Template PDF not found."}), 500

    def get_mod(score):
        return f"+{(score - 10) // 2}" if score >= 10 else str((score - 10) // 2)

    # Map model fields to PDF form fields
    field_map = {
        "CharacterName": player.name,
        "RACE": player.species,
        "CLASS  LEVEL": player.character_class,
        "BACKGROUND": player.background or "",
        "ALIGNMENT": player.alignment or "",
        "STR": str(player.strength),
        "DEX": str(player.dexterity),
        "CON": str(player.constitution),
        "INT": str(player.intelligence),
        "WIS": str(player.wisdom),
        "CHA": str(player.charisma),
        "STRmod": get_mod(player.strength),
        "DEXmod ": get_mod(player.dexterity),
        "CONmod": get_mod(player.constitution),
        "INTmod": get_mod(player.intelligence),
        "WISmod": get_mod(player.wisdom),
        "CHamod": get_mod(player.charisma),
        "AC": str(player.armor_class),
        "Init": str(player.initiative),
        "Speed": str(player.speed),
        "MaxHP": str(player.hit_points),
        "CurrentHP": str(player.hit_points),
        "FeaturesTraits": player.description or "",
        "Backstory": player.backstory or "",
        "Equipment": player.equipment or "",
        "ProficienciesLang": (player.skills or "") + " " + (player.languages or ""),
    }

    try:
        doc = fitz.open(template_path)
        for page in doc:
            for widget in page.widgets():
                if widget.field_name in field_map:
                    widget.field_value = field_map[widget.field_name]
                    widget.update()
        
        pdf_bytes = doc.write()
        doc.close()
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{player.name.replace(' ', '_')}_Character_Sheet.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
