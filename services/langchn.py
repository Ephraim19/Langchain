from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langgraph.graph import MessagesState,StateGraph
from langchain_core.tools import tool


from typing import List, Dict, Any
from dotenv import load_dotenv
import os
import getpass
import bs4
import json

# Load environment variables
load_dotenv()

# Set API key if not present
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")


def load_and_split_documents(url:str):
    
    loader = WebBaseLoader(
        web_paths=(url,),
        bs_kwargs={}
    )
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)
    
    return all_splits


def load_local_documents(docs_dir="./documents"):
    """Load documents from a local directory."""
    # Create directory with sample if it doesn't exist
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        with open(f"{docs_dir}/sample.txt", "w") as f:
            f.write("This is a sample document for the RAG system.")
    
    loader = DirectoryLoader(docs_dir, glob="**/*.txt")
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)
    
    return all_splits


def retrieve_documents(question:str, url:str, use_web=True) -> List[Document]:
    """Retrieve relevant documents based on the query."""
    try:
        # Load documents
        if use_web:
            documents = load_and_split_documents(url)
        else:
            documents = load_local_documents()
        
        # Initialize embeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Use FAISS for vector storage (in memory)
        vector_store = FAISS.from_documents(documents=documents, embedding=embeddings)
        
        # Retrieve relevant documents
        retrieved_docs = vector_store.similarity_search(question, k=4)
        
        return retrieved_docs
    
    except Exception as e:
        print(f"Error in retrieve_documents: {str(e)}")
        return []

# @tool(name="LangChainRAG", description="LangChain RAG system")
def generate_answer(query: str, context_docs: List[Document]) -> str:
    """Generate an answer based on retrieved documents."""
    try:
        # Initialize model
        model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
        
        graph_builder = StateGraph(MessagesState)
        
        # Create prompt
        template = """Answer the question based on the following context:
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Prepare context content
        docs_content = "\n\n".join(doc.page_content for doc in context_docs)
        
        # Generate response
        messages = prompt.invoke({"question": query, "context": docs_content})
        response = model.invoke(messages)
        
        return response.content
    
    except Exception as e:
        print(f"Error in generate_answer {str(e)}")
        return f"An error occurred: {str(e)}"




def LangChainRAG(url,question):

    try:
        # Query, search and answer
        # question = "carbon footprint"
        print(f"\nQuestion: {question}")
        
        retrieved_docs = retrieve_documents(question, url, use_web=True)
        print(f"\nRetrieved {len(retrieved_docs)} documents.")
        
        answer = generate_answer(question, retrieved_docs)
        print(f"\nAnswer: {answer}")
        
        return answer
    
    except Exception as e:
        print(f"Error in LangChainRAG: {str(e)}")
        return {"answer": f"An error occurred: {str(e)}", "sources": []}


# Run the RAG pipeline
if __name__ == "__main__":
    result = LangChainRAG()
    print(json.dumps(result, indent=2))
    
def LangChainService():
# Initialize model
  model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
  system_template = "Translate the following from English into {language}"
  prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
  )
  
  prompt = prompt_template.invoke({"language": "Italian", "text": "hi!"})
  prompt.to_messages()
  response = model.invoke(prompt)
  return response

