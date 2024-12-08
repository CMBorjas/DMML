from flask import Blueprint, render_template, request, jsonify
from app.models.ai import generate_suggestion
from app.models.npc import NPC
from app import db
import random
from app.models.campaign import CampaignLog
from app.models.player_profile import PlayerProfile

# Create a blueprint
main_bp = Blueprint('main', __name__)

# Add a new route to chat with an NPC -------------------------------------------------------------
@main_bp.route('/')
def index():
    return render_template('index.html')

# Add a new route to chat with an NPC -------------------------------------------------------------
@main_bp.route('/generate_suggestion', methods=['POST'])
def get_suggestion():
    data = request.get_json()
    query = data.get('query')
    if query:
        suggestion = generate_suggestion(query)
        return jsonify({"suggestion": suggestion}), 200
    return jsonify({"error": "Query missing"}), 400

# Add a new route to chat with an NPC -------------------------------------------------------------
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

# Add a new route to chat with an NPC -------------------------------------------------------------
@main_bp.route('/npc/<int:npc_id>', methods=['GET'])
def get_npc(npc_id):
    npc = NPC.query.get_or_404(npc_id)
    return jsonify(npc.to_dict())

# Add a new route to chat with an NPC -------------------------------------------------------------
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

# Add a new route to chat with an NPC -------------------------------------------------------------
@main_bp.route('/npc/<int:npc_id>', methods=['DELETE'])
def delete_npc(npc_id):
    npc = NPC.query.get_or_404(npc_id)
    db.session.delete(npc)
    db.session.commit()
    return jsonify({"message": "NPC deleted"}), 204

# Add a new route to chat with an NPC -------------------------------------------------------------
@main_bp.route('/npc/<int:npc_id>/chat', methods=['POST'])
def chat_with_npc(npc_id):
    npc = NPC.query.get_or_404(npc_id)
    player_input = request.json.get('input', '').strip()
    if not player_input:
        return jsonify({"error": "Input is required"}), 400

    # Retrieve recent interactions (e.g., last 5 chat logs)
    recent_interactions = npc.chat_history.split("\n")[-5:]  # Get the last 5 interactions

    # Build the query with multi-turn context
    context_query = f"NPC Name: {npc.name}\nRecent Interactions:\n{recent_interactions}\n\nPlayer Query: {player_input}\nResponse:"

    # Generate the response using RAG
    response = generate_suggestion(context_query).strip()

    # Update chat history
    new_message = f"Player: {player_input}\n{npc.name}: {response}\n\n"
    npc.chat_history = (npc.chat_history or "") + new_message
    db.session.commit()

    return jsonify({"npc_response": response, "chat_history": npc.chat_history})


# Helper function to generate a random NPC --------------------------------------------------------
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

# Add a new route to generate a random NPC --------------------------------------------------------
@main_bp.route('/npc/generate', methods=['POST'])
def generate_npc():
    npc = generate_random_npc()
    db.session.add(npc)
    db.session.commit()
    return jsonify(npc.to_dict()), 201

# Add a new route to get all NPCs ----------------------------------------------------------------
@main_bp.route('/npc', methods=['GET'])
def get_all_npcs():
    npcs = NPC.query.all()
    return jsonify([npc.to_dict() for npc in npcs])

# Add a new route to seed the database with example NPCs ------------------------------------------
@main_bp.route('/debug/campaign_logs', methods=['GET'])
def debug_campaign_logs():
    campaign_logs = CampaignLog.query.all()
    return jsonify([
        {
            "id": log.id,
            "narrative": log.narrative,
            "encounters": log.encounters,
            "npc_details": log.npc_details,
        }
        for log in campaign_logs
    ])

# Add a new route to seed the database with example NPCs ------------------------------------------
@main_bp.route('/debug/seed_campaign_logs', methods=['POST'])
def seed_campaign_logs():
    # Check if campaign logs already exist
    if CampaignLog.query.count() > 0:
        return jsonify({"message": "Campaign logs already exist. No need to seed again."}), 200

    # Example campaign logs
    logs = [
        {
            "narrative": "The party entered the haunted forest seeking the lost artifact.",
            "encounters": "They were ambushed by a pack of wolves and a band of goblins.",
            "npc_details": "They met a mysterious ranger named Kaelen who offered to guide them."
        },
        {
            "narrative": "The party reached the ancient ruins and found the artifact.",
            "encounters": "They had to solve a magical puzzle to unlock the door.",
            "npc_details": "An old historian NPC named Elenna shared knowledge about the artifact."
        }
    ]

    for log in logs:
        campaign_log = CampaignLog(
            narrative=log["narrative"],
            encounters=log["encounters"],
            npc_details=log["npc_details"]
        )
        db.session.add(campaign_log)
    
    db.session.commit()
    return jsonify({"message": "Campaign logs seeded successfully."}), 201

# Add a new route to get all NPCs ----------------------------------------------------------------
@main_bp.route('/player', methods=['POST'])
def create_player():
    data = request.get_json()
    player = PlayerProfile(
        name=data['name'],
        species=data['species'],
        subspecies=data.get('subspecies', ''),
        player_class=data['player_class'],
        background=data.get('background', ''),
        alignment=data.get('alignment', ''),
        strength=data.get('strength', 10),
        dexterity=data.get('dexterity', 10),
        constitution=data.get('constitution', 10),
        intelligence=data.get('intelligence', 10),
        wisdom=data.get('wisdom', 10),
        charisma=data.get('charisma', 10),
        skills=data.get('skills', ''),
        tool_proficiencies=data.get('tool_proficiencies', ''),
        languages=data.get('languages', ''),
        hit_points=data.get('hit_points', 10),
        armor_class=data.get('armor_class', 10),
        speed=data.get('speed', 30),
        initiative=data.get('initiative', 0),
        saving_throws=data.get('saving_throws', ''),
        equipment=data.get('equipment', ''),
        weapons=data.get('weapons', ''),
        spells=data.get('spells', ''),
        description=data.get('description', ''),
        backstory=data.get('backstory', ''),
        campaign_id=data.get('campaign_id', None)
    )
    db.session.add(player)
    db.session.commit()
    return jsonify(player.to_dict()), 201

# Add a new route to get all NPCs ----------------------------------------------------------------
@main_bp.route('/player/<int:player_id>', methods=['GET'])
def get_player(player_id):
    player = PlayerProfile.query.get_or_404(player_id)
    return jsonify(player.to_dict())

# Add a new route to get all NPCs ----------------------------------------------------------------
@main_bp.route('/player', methods=['GET'])
def get_all_players():
    players = PlayerProfile.query.all()
    return jsonify([player.to_dict() for player in players])

# Add a new route to get all NPCs ----------------------------------------------------------------
@main_bp.route('/player/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    data = request.get_json()
    player = PlayerProfile.query.get_or_404(player_id)
    player.name = data.get('name', player.name)
    player.species = data.get('species', player.species)
    player.subspecies = data.get('subspecies', player.subspecies)
    player.player_class = data.get('player_class', player.player_class)
    player.background = data.get('background', player.background)
    player.alignment = data.get('alignment', player.alignment)
    player.strength = data.get('strength', player.strength)
    player.dexterity = data.get('dexterity', player.dexterity)
    player.constitution = data.get('constitution', player.constitution)
    player.intelligence = data.get('intelligence', player.intelligence)
    player.wisdom = data.get('wisdom', player.wisdom)
    player.charisma = data.get('charisma', player.charisma)
    player.skills = data.get('skills', player.skills)
    player.tool_proficiencies = data.get('tool_proficiencies', player.tool_proficiencies)
    player.languages = data.get('languages', player.languages)
    player.hit_points = data.get('hit_points', player.hit_points)
    player.armor_class = data.get('armor_class', player.armor_class)
    player.speed = data.get('speed', player.speed)
    player.initiative = data.get('initiative', player.initiative)
    player.saving_throws = data.get('saving_throws', player.saving_throws)
    player.equipment = data.get('equipment', player.equipment)
    player.weapons = data.get('weapons', player.weapons)
    player.spells = data.get('spells', player.spells)
    player.description = data.get('description', player.description)
    player.backstory = data.get('backstory', player.backstory)
    db.session.commit()
    return jsonify(player.to_dict())

# Add a new route to get all NPCs ----------------------------------------------------------------
@main_bp.route('/player/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    player = PlayerProfile.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return jsonify({"message": "Player profile deleted"}), 204

# Create a player profile
@main_bp.route('/player_profile', methods=['POST'])
def create_player_profile():
    try:
        data = request.json
        print("Received data:", data)  # Log incoming data for debugging
        
        # Validate required fields
        required_fields = ['name', 'species', 'character_class', 'player_class', 'stats']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create player profile
        player = PlayerProfile(
            name=data['name'],
            species=data['species'],
            character_class=data['character_class'],
            player_class=data['player_class'],
            background=data.get('background', ''),
            alignment=data.get('alignment', ''),
            strength=data['stats']['STR'],
            dexterity=data['stats']['DEX'],
            constitution=data['stats']['CON'],
            intelligence=data['stats']['INT'],
            wisdom=data['stats']['WIS'],
            charisma=data['stats']['CHA']
        )
        db.session.add(player)
        db.session.commit()
        return jsonify(player.to_dict()), 201
    except KeyError as e:
        print("KeyError:", str(e))  # Log specific missing key
        return jsonify({"error": f"Missing required key: {str(e)}"}), 400
    except Exception as e:
        print("Unexpected error:", str(e))  # Log unexpected errors
        return jsonify({"error": "An unexpected error occurred"}), 500

# Retrieve all player profiles
@main_bp.route('/player_profiles', methods=['GET'])
def get_all_player_profiles():
    players = PlayerProfile.query.all()
    return jsonify([player.to_dict() for player in players])

# Retrieve a single player profile
@main_bp.route('/player_profile/<int:player_id>', methods=['GET'])
def get_player_profile(player_id):
    player = PlayerProfile.query.get_or_404(player_id)
    return jsonify(player.to_dict())

# Update a player profile
@main_bp.route('/player_profile/<int:player_id>', methods=['PUT'])
def update_player_profile(player_id):
    player = PlayerProfile.query.get_or_404(player_id)
    data = request.get_json()
    player.name = data.get('name', player.name)
    player.species = data.get('species', player.species)
    player.character_class = data.get('character_class', player.character_class)
    player.alignment = data.get('alignment', player.alignment)
    player.stats = data.get('stats', player.stats)
    player.inventory = data.get('inventory', player.inventory)
    player.actions = data.get('actions', player.actions)
    db.session.commit()
    return jsonify(player.to_dict())

# Delete a player profile
@main_bp.route('/player_profile/<int:player_id>', methods=['DELETE'])
def delete_player_profile(player_id):
    player = PlayerProfile.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return jsonify({"message": "Player profile deleted"}), 204

# Add a new route to generate a quest for an NPC --------------------------------------------------
@main_bp.route('/npc/<int:npc_id>/generate_quest', methods=['POST'])
def generate_quest_for_npc(npc_id):
    npc = NPC.query.get_or_404(npc_id)  # Fetch the NPC or return 404 if not found
    data = request.get_json()  # Parse the JSON request
    location = data.get('location', 'unknown location')  # Get the location from the request

    # Generate a quest description (customize as needed)
    quest_description = (
        f"{npc.name} has assigned you a quest to investigate strange occurrences in the {location}. "
        f"Prepare to face challenges and uncover hidden secrets."
    )

    # Add the quest to the NPC's chat history
    new_message = f"{npc.name}: {quest_description}\n\n"
    npc.chat_history = (npc.chat_history or "") + new_message

    # Save changes to the database
    db.session.commit()

    # Return the quest and updated chat history
    return jsonify({"quest": quest_description, "chat_history": npc.chat_history}), 200

@main_bp.route('/npc/<int:npc_id>/generate_loot', methods=['POST'])
def generate_loot_for_npc(npc_id):
    npc = NPC.query.get_or_404(npc_id)  # Fetch the NPC or return 404 if not found

    # Generate loot (customize as needed)
    loot_items = [
        "a magical sword",
        "a bag of gold coins",
        "a rare potion",
        "a mysterious artifact",
        "a scroll of ancient wisdom",
    ]
    generated_loot = ", ".join(random.sample(loot_items, 2))  # Randomly pick two items

    # Add the loot generation to the NPC's chat history
    new_message = f"{npc.name}: I have prepared the following loot for you: {generated_loot}\n\n"
    npc.chat_history = (npc.chat_history or "") + new_message

    # Save changes to the database
    db.session.commit()

    # Return the generated loot and updated chat history
    return jsonify({"loot": generated_loot, "chat_history": npc.chat_history}), 200
