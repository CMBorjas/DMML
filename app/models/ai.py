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

# Function to set up the retrieval chain for LangChain
def setup_retrieval_chain():
    # Get campaign data (narrative, encounters, NPCs)
    campaign_data = get_campaign_data()  
    vectorstore = FAISS.from_texts(campaign_data, embeddings)
    retrieval_chain = RetrievalQA.from_chain_and_vectorstore(llm, vectorstore)
    return retrieval_chain

# Function to get AI-powered narrative suggestions based on campaign history
def generate_suggestion(query):
    retrieval_chain = setup_retrieval_chain()
    response = retrieval_chain.run(query)
    return response
