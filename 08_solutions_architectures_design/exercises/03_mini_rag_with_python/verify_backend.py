from src.orchestrator import RAGOrchestrator
import time

def test_pipeline():
    print("Initializing Orchestrator...")
    orchestrator = RAGOrchestrator()
    
    # Ingest if needed (already in init, but let's be sure)
    print("Checking documents...")
    orchestrator.retrieval_system.ingest_documents("./documents")
    
    query = "What is Algoesis?"
    print(f"\nQuerying: {query}")
    
    history = []
    
    try:
        stream, sources = orchestrator.query(query, history)
        
        print("\n--- Sources ---")
        for s in sources:
            print(f"- {s.source} (Preview: {s.content[:50]}...)")
            
        print("\n--- Response ---")
        full_response = ""
        for chunk in stream:
            print(chunk, end="", flush=True)
            full_response += chunk
        print("\n\nTest Complete!")
        
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_pipeline()
