import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from rag import RetrievalSystem
import chromadb
from rank_bm25 import BM25Okapi

def test_retrieval_logic():
    print("--- Testing Retrieval Logic ---")
    retriever = RetrievalSystem(chroma_path="./chroma_db")
    
    # Force re-ingestion to ensure new chunking is applied if not already
    # (In a real app we might want to trigger this manually, but here we want to test the new logic)
    print("Re-ingesting for test consistency...")
    retriever.ingest_documents("./documents")
    
    query = "features of Algoesis"
    print(f"\nQuery: '{query}'")

    # 1. Test Semantic Search (Directly via Chroma collection)
    print("\n[TEST] Semantic Search Only (ChromaDB)")
    try:
        results = retriever.collection.query(query_texts=[query], n_results=3)
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                print(f"  {i+1}. {doc[:60]}... (Source: {meta['source']})")
        else:
            print("  No semantic results found.")
    except Exception as e:
        print(f"  Semantic search error: {e}")

    # 2. Test Keyword Search (Directly via BM25 instance)
    print("\n[TEST] Keyword Search Only (BM25)")
    if retriever.bm25:
        tokenized_query = query.split(" ")
        # Get raw scores
        doc_scores = retriever.bm25.get_scores(tokenized_query)
        # Get top 3 indices
        top_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:3]
        
        for i, idx in enumerate(top_indices):
            score = doc_scores[idx]
            if score > 0:
                doc = retriever.documents_content[idx]
                meta = retriever.documents_metadata[idx]
                print(f"  {i+1}. Score: {score:.3f} - {doc[:60]}... (Source: {meta['source']})")
            else:
                print(f"  {i+1}. Score 0.0 - (No match)")
    else:
        print("  BM25 not initialized.")

    # 3. Test Hybrid Search (via search method)
    print("\n[TEST] Hybrid Search (Combined)")
    hybrid_results = retriever.search(query, top_k=5)
    for i, res in enumerate(hybrid_results):
        score_display = f"{res.score:.3f}" if res.score is not None else "N/A"
        print(f"  {i+1}. [{res.score}] {res.content[:60]}... (Source: {res.source})")

if __name__ == "__main__":
    test_retrieval_logic()
