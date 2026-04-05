import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from dotenv import load_dotenv
import os
import chromadb
from sentence_transformers import CrossEncoder

load_dotenv()

client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])

def embed(texts,batch_size=2048):
    all_embeddings = []
    for i in range(0,len(texts),batch_size):
        batch = texts[i:i+2048]
        response = client.embeddings.create(
        model = "text-embedding-3-small",
        input = batch
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings

chroma_client = chromadb.PersistentClient(path = "/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/rag/vector_store")
collection = chroma_client.get_or_create_collection(name = "AI_book_oreily",metadata = {"hnsw:space":"cosine"})
if collection.count() == 0:
    doc = pymupdf.open("/Users/sagrikasrivastav/Desktop/Studying phase/Books/AI Engineering.pdf")
    pdf_text = ""
    for i in range(len(doc)):
        text = doc[i].get_text()
        pdf_text += text 

    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500,chunk_overlap = 50)
    chunks = text_splitter.split_text(pdf_text)

    embeddings = embed(chunks)
    collection.add(documents = chunks,
    embeddings  = embeddings,
    ids = [f"chunk_{i}" for i in range(0,len(chunks))])