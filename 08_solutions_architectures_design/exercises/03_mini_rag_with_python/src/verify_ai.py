import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from rag import RetrievalSystem
from llm import LLMClient
import chromadb

def setup_data():
    print("--- Setting up Dummy Data in Chroma ---")
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(name="documents")
        
        # Check if empty, if so add dummy
        if collection.count() == 0:
            print("Adding 'Algoesis' document to Chroma...")
            with open("documents/algoesis.txt", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split roughly (very naive)
            chunks = [content[i:i+500] for i in range(0, len(content), 500)]
            ids = [f"doc_{i}" for i in range(len(chunks))]
            metadatas = [{"source": "algoesis.txt", "chunk_id": i} for i in range(len(chunks))]
            
            collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            print(f"Added {len(chunks)} chunks.")
        else:
            print(f"Collection already has {collection.count()} documents.")
            
    except Exception as e:
        print(f"Setup failed: {e}")

def verify_retrieval():
    print("\n--- Verifying Hybrid Retriever ---")
    try:
        retriever = RetrievalSystem(chroma_path="./chroma_db")
        query = "What is Algoesis?"
        results = retriever.search(query, top_k=3)
        
        print(f"Query: {query}")
        print(f"Found {len(results)} results.")
        for res in results:
            score_val = res.score if res.score is not None else 0.0
            print(f"[{res.source.upper()}] Score: {score_val:.2f} - {res.content[:50]}...")
            
        return results
    except Exception as e:
        print(f"Retrieval failed: {e}")
        return []

def verify_llm(context_results):
    print("\n--- Verifying LLM Client ---")
    try:
        client = LLMClient()
        
        context_str = "\n".join([r.content for r in context_results])
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the context provided to answer."},
            {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: What is Algoesis?"}
        ]
        
        print("Sending request to LLM (localhost:1234)...")
        # Non-streaming for test
        response = client.chat(messages)
        print(f"LLM Response:\n{response}")
        
    except Exception as e:
        print(f"LLM verification failed: {e}")
        print("Ensure LM Studio is running on port 1234 with a model loaded!")

if __name__ == "__main__":
    setup_data()
    results = verify_retrieval()
    if results:
        verify_llm(results)
    else:
        print("Skipping LLM test due to retrieval failure.")
