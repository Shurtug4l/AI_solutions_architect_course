from typing import List, Generator
from rag import RetrievalSystem
from llm import LLMClient
from models import ChatMessage
import os

class RAGOrchestrator:
    def __init__(self):
        self.retrieval_system = RetrievalSystem()
        self.llm_client = LLMClient()
        
        # Ensure we have some data
        docs_path = "../documents" if os.path.exists("../documents") else "./documents"
        
        if not self.retrieval_system.documents_content:
            try:
                self.retrieval_system.ingest_documents(docs_path)
            except Exception as e:
                print(f"Ingestion failed or empty: {e}")

    def query(self, user_message: str, history: List[dict]):
        # 1. Retrieve context
        try:
            results = self.retrieval_system.search(user_message, top_k=2)
            context_str = "\n\n".join([f"Source: {r.source}\nContent: {r.content}" for r in results])
            print(f"Retrieved {len(results)} chunks.")
        except Exception as e:
            print(f"Retrieval error: {e}")
            context_str = ""
            results = []

        # 2. Construct System Prompt
        system_prompt = f"""You are a helpful local assistant. 
Use the following context to answer the user's question. 
If the context doesn't contain the answer, say you don't know, but try to be helpful.

Context:
{context_str}
"""

        # 3. Prepare Messages
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            if msg["role"] in ["user", "assistant"]:
                messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})

        # 4. Stream Response
        stream = self.llm_client.chat_stream(messages)
        
        def generator():
            if stream:
                for chunk in stream:
                    yield chunk
            else:
                yield "Error: Could not connect to LLM."
                
        return generator(), results
