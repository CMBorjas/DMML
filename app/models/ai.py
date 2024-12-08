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

# Function to set up the retrieval chain for LangChain------------------------
def setup_retrieval_chain():
    embeddings = OpenAIEmbeddings()
    campaign_data = get_campaign_data()
    if not campaign_data:
        raise ValueError("No campaign data found! Please add some logs.")
    
    vectorstore = FAISS.from_texts(campaign_data, embeddings)
    retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever()
    )
    return retrieval_chain


# Function to get AI-powered narrative suggestions based on campaign history ---------------------
def generate_suggestion(query):
    retrieval_chain = setup_retrieval_chain()
    result = retrieval_chain.invoke({"query": query})  # Ensure we get the correct response format

    # Log the raw result for debugging
    print("Raw LangChain result:", result)

    # Extract the 'result' key from the response dictionary
    if isinstance(result, dict) and "result" in result:
        return result["result"]
    elif isinstance(result, str):
        return result  # If it's already a string, return it
    else:
        raise ValueError(f"Unexpected response format from LangChain: {result}")

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
