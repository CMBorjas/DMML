from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, OpenAI
from app.models.campaign import get_campaign_data
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

# Initialize OpenAI with the API key
llm = OpenAI(openai_api_key=openai_api_key)

# Initialize the vector store and embeddings
embeddings = OpenAIEmbeddings()

# Function to set up the retrieval chain for LangChain---------------------------------------------
def setup_retrieval_chain():
    embeddings = OpenAIEmbeddings()
    campaign_data = get_campaign_data()  # Retrieve campaign logs
    if not campaign_data:
        raise ValueError("No campaign data found! Please add some logs.")
    
    # Use embeddings to create a vector store with prioritization logic
    vectorstore = FAISS.from_texts(campaign_data, embeddings)
    retriever = vectorstore.as_retriever()
    
    # Refine retriever with filters (if applicable) or sort by relevance
    retriever.search_kwargs = {"k": 5}  # Retrieve the top 5 most relevant logs

    retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever
    )
    return retrieval_chain

# Function to get AI-powered narrative suggestions based on campaign history ------------------------------------------
def generate_suggestion(query, npc_name=None, recent_interactions=None):
    retrieval_chain = setup_retrieval_chain()

    # Build a richer prompt using the recent interactions and NPC context
    if npc_name and recent_interactions:
        context = (
            f"You are {npc_name}, an NPC in a tabletop role-playing game. Stay in character and respond naturally.\n\n"
            f"Recent interactions:\n{recent_interactions}\n\n"
            f"Player Query: {query}\n"
        )
    else:
        context = query  # Use the raw query if no additional context is available

    # Invoke LangChain with the context
    result = retrieval_chain.invoke({"query": context})

    # Debug raw result
    print("Raw LangChain result:", result)

    # Extract and return the result
    if isinstance(result, dict) and "result" in result:
        return result["result"]
    elif isinstance(result, str):
        return result
    else:
        raise ValueError(f"Unexpected response format: {result}")

# Function to generate AI-powered quest suggestions based on NPC and location ---------------------
def generate_quest(npc_name, location):
    """
    Generate a quest request from an NPC based on their name and location.
    """
    prompt = (
        f"{npc_name}, a knowledgeable NPC located in {location}, "
        "wants to assign a task to adventurers. Generate a detailed quest they might request."
    )
    return generate_suggestion(prompt)

# Function to generate AI-powered loot suggestions based on quest name ----------------------------
def generate_loot(quest_name):
    """
    Generate loot rewards for a completed quest based on the quest name.
    """
    prompt = (
        f"Based on the completion of the quest '{quest_name}', "
        "generate a suitable loot reward for adventurers."
    )
    return generate_suggestion(prompt)
