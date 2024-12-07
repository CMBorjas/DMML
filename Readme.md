# DMML
An AI-driven tool designed for Dungeon Masters (DMs) in tabletop role-playing games. 

## Project description
Proposal: AI-Powered Dungeon Master Assistant with RAG
High-Level Concept: An AI-driven tool designed for Dungeon Masters (DMs) in tabletop role-playing games. The tool will leverage LangChain's Retrieval-Augmented Generation (RAG) to fetch relevant information from a campaign database and enhance storytelling in real-time. Using LLMs, the assistant will generate narrative suggestions, enemy encounters, and loot tailored to the game's current state based on prior campaign history and player choices.
Front End: A Flask web interface enables Dungeon Masters to manage game sessions, import custom maps, and view AI-generated suggestions in real-time. The interface will allow for intuitive interaction, such as token placement on a visual map and dialogue generation for non-player characters (NPCs).
Database:
*	Player Profiles: Stores character information 
    * Stats, Skills, Background
    * Inventory
    * Actions
*	Campaign Logs: 
    * Stores the narrative history, encounters, and NPC details.

## Retrieval-Augmented Generation (RAG) 
- This model will retrieve relevant parts of the campaign history to generate contextually appropriate suggestions for ongoing gameplay.
Tools:
*	LangChain: To query the campaign database using RAG and generate context-aware narratives based on the retrieved information.
    *	Example: “Jenny (Witch in the woods):  I have a request for you complete. I need a live troll to study their habits, and to fortify the defenses of the kingdom” 


## How to setup enivronment and docker
* Step 1: Activate the environment
```bash
    dmml\Scripts\activate
```
* Step 2: Create the docker container
```bash
docker-compose up --build
```
* Step 3: Access the website
```
http://127.0.0.1:5000/
```

## Folder Structure:
```
/DMML
│
├── /app                  # Main application directory
│   ├── __init__.py       # Initialize the Flask app
│   ├── routes.py         # API and Flask route definitions
│   ├── templates/        # HTML templates for Flask
│   │   └── index.html    # The main web page
│   ├── static/           # Static assets (CSS, JS, images, etc.)
│   │   └── style.css     # Styling for your app
│   └── models/           # Models for database and AI generation
│       ├── profile.py    # Player profile model
│       ├── campaign.py   # Campaign log model
│       └── ai.py         # LangChain setup and AI-powered functions
├── /dmml                 # Environment
│
├── /instance             # Store your campaign database
│   └── data.db           # SQLite or other format for storing logs 
│
├── /migrations
|   ├── / _pychache
|   ├── /Versions
│   ├── alembic.ini
|   ├── /env.py
|   ├── README             # Single-database configuration for Flask. 
|   └── script.py.mako
|
├── Dockerfile        # Docker configuration for Flask app
├── docker-compose.yml# Docker Compose file for multi-container setup
├──.env               # Environment variables
├──.gitignore         # Git ignore file
├── requirements.txt  # Python dependencies
└── run.py            # Entry point to run the app (Flask development server)

```
## Steps to meet proposal

1. Front End Enhancements:

    Add functionality to import custom maps and allow token placement.

2. Player Profiles:

    Develop a database model for Player Profiles, including stats, inventory, and actions.

3. Dynamic Quest and Loot Generation:

    Extend LangChain's functionality to generate quests and loot, tailored to the current game context.

4. Example Use Case:

    Implement features like generating a quest or request from an NPC (e.g., Jenny the Witch).

## Future goals
1. Refine AI Responses:

    Modify the prompt template sent to LangChain to include clear instructions for generating creative and relevant responses.
    For example, you could structure it like this:

    NPC Context: {npc_context}
    Chat History: {chat_history}
    Player says: {player_input}
    NPC should reply in-character with relevant information or actions.

2. UI Updates:

    Allow players to review the full chat history in a scrollable or expandable section.
    Add options to reset or clear an NPC's chat history.

3. Handle Missing or Ambiguous Player Input:

    Provide feedback if the player's input isn't clear or relevant.
    You could add hints or examples of valid questions in the UI.

4. Persistence and Campaign Integration:

    Save all interactions to the campaign log for later reference.
    Use these logs to inform NPCs' future behavior or interactions in the campaign.