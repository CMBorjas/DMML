from flask import Blueprint, render_template, request, jsonify
from app.models.ai import generate_suggestion
from app.models.npc import NPC
from app import db
import random

# Create a blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/generate_suggestion', methods=['POST'])
def get_suggestion():
    data = request.get_json()
    query = data.get('query')
    if query:
        suggestion = generate_suggestion(query)
        return jsonify({"suggestion": suggestion}), 200
    return jsonify({"error": "Query missing"}), 400

@main_bp.route('/npc', methods=['POST'])
def create_npc():
    data = request.get_json()
    npc = NPC(
        name=data['name'],
        role=data['role'],
        alignment=data.get('alignment', ''),
        stats=data.get('stats', {}),
        abilities=data.get('abilities', ''),
        spells=data.get('spells', ''),
        racial_features=data.get('racial_features', ''),
        description=data.get('description', '')
    )
    db.session.add(npc)
    db.session.commit()
    return jsonify(npc.to_dict()), 201

@main_bp.route('/npc/<int:npc_id>', methods=['GET'])
def get_npc(npc_id):
    npc = NPC.query.get_or_404(npc_id)
    return jsonify(npc.to_dict())

@main_bp.route('/npc/<int:npc_id>', methods=['PUT'])
def update_npc(npc_id):
    data = request.get_json()
    npc = NPC.query.get_or_404(npc_id)
    npc.name = data.get('name', npc.name)
    npc.role = data.get('role', npc.role)
    npc.alignment = data.get('alignment', npc.alignment)
    npc.stats = data.get('stats', npc.stats)
    npc.abilities = data.get('abilities', npc.abilities)
    npc.spells = data.get('spells', npc.spells)
    npc.racial_features = data.get('racial_features', npc.racial_features)
    npc.description = data.get('description', npc.description)
    db.session.commit()
    return jsonify(npc.to_dict())

@main_bp.route('/npc/<int:npc_id>', methods=['DELETE'])
def delete_npc(npc_id):
    npc = NPC.query.get_or_404(npc_id)
    db.session.delete(npc)
    db.session.commit()
    return jsonify({"message": "NPC deleted"}), 204

@main_bp.route('/npc/<int:npc_id>/chat', methods=['POST'])
def chat_with_npc(npc_id):
    npc = NPC.query.get_or_404(npc_id)
    player_input = request.json.get('input', '')
    context = f"NPC: {npc.name}, Role: {npc.role}, Abilities: {npc.abilities}, Spells: {npc.spells}, Racial Features: {npc.racial_features}"
    response = generate_suggestion(f"{context}. Player says: {player_input}")
    return jsonify({"npc_response": response})

# Helper function to generate a random NPC
def generate_random_npc():
    return NPC(
        name=random.choice(["Dora Toreral", "Flarin Dusk", "Eryn Leafwalker"]),
        role=random.choice(["Minstrel", "Warrior", "Sorcerer"]),
        alignment=random.choice(["Lawful Good", "Neutral", "Chaotic Evil"]),
        stats={
            "STR": random.randint(8, 18),
            "DEX": random.randint(8, 18),
            "CON": random.randint(8, 18),
            "INT": random.randint(8, 18),
            "WIS": random.randint(8, 18),
            "CHA": random.randint(8, 18),
        },
        abilities="Special abilities placeholder.",
        spells="Spells placeholder.",
        racial_features="Racial features placeholder.",
        description="An NPC created with default random values."
    )

@main_bp.route('/npc/generate', methods=['POST'])
def generate_npc():
    npc = generate_random_npc()
    db.session.add(npc)
    db.session.commit()
    return jsonify(npc.to_dict()), 201

@main_bp.route('/npc', methods=['GET'])
def get_all_npcs():
    npcs = NPC.query.all()
    return jsonify([npc.to_dict() for npc in npcs])