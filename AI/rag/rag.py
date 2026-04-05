import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from dotenv import load_dotenv
import os
import chromadb
from sentence_transformers import CrossEncoder
from ingestion import collection

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

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
def retrieval(message):
    print("I've been called!")
    query = embed([message])
    print("I've!")
    results = collection.query(
    query_embeddings = query,
    n_results = 5)
    print("I reached here1!")
    retrieved_chunks = results["documents"][0]
    pairs = [(message,chunk) for chunk in retrieved_chunks]
    scores = reranker.predict(pairs)
    ranked_chunks = sorted(zip(scores,retrieved_chunks),key = lambda x: x[0],reverse = True)
    print("I reached here2!")
    for score,chunk in ranked_chunks:
        print("score:",score)
        print("chunk:",chunk)
        print("------------------------------")
    final_retrieved = ""
    for score,chunk in ranked_chunks:
        if score > 0:
            final_retrieved += chunk + "\n\n"
    return final_retrieved
    







