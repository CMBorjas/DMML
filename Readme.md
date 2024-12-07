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
