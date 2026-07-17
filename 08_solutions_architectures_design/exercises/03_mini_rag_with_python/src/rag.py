import os
import glob
import uuid
import chromadb
from rank_bm25 import BM25Okapi
from typing import List
from models import RetrievalResult

class RetrievalSystem:
    def __init__(self, chroma_path: str = "./chroma_db"):
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(name="documents")
        self.bm25 = None
        self.documents_content = [] # Cache for BM25: list of strings (chunks)
        self.documents_metadata = [] # list of metadata dicts
        self._load_existing_data()

    def _load_existing_data(self):
        # Load existing data from Chroma to initialize BM25
        try:
            result = self.collection.get()
            if result and result['documents']:
                self.documents_content = result['documents']
                self.documents_metadata = result['metadatas']
                tokenized_corpus = [doc.split(" ") for doc in self.documents_content]
                self.bm25 = BM25Okapi(tokenized_corpus)
        except Exception as e:
            print(f"Error loading existing data: {e}")

    def ingest_documents(self, folder_path: str):
        print(f"Ingesting documents from {folder_path}...")
        # Simple text ingestion
        files = glob.glob(os.path.join(folder_path, "*.txt"))
        
        new_docs = []
        new_metadatas = []
        new_ids = []

        for file_path in files:
            filename = os.path.basename(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Sliding Window Chunking
                chunk_size = 1000
                chunk_overlap = 200
                chunks = []
                start = 0
                while start < len(content):
                    end = start + chunk_size
                    chunk = content[start:end]
                    
                    # If we are not at the end, try to break at the last space
                    if end < len(content):
                        last_space = chunk.rfind(' ')
                        if last_space != -1:
                            end = start + last_space
                            chunk = content[start:end]
                    
                    chunks.append(chunk.strip())
                    
                    # Calculate step
                    step = len(chunk) - chunk_overlap
                    # Ensure positive step to avoid infinite loop
                    if step <= 0:
                        start += len(chunk) # Just move past this chunk
                    else:
                        start += step
                
                for i, chunk in enumerate(chunks):
                    if not chunk: continue
                    new_docs.append(chunk)
                    new_metadatas.append({"source": filename, "chunk_index": i})
                    new_ids.append(f"{filename}_{i}_{uuid.uuid4().hex[:8]}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

        if new_docs:
            self.collection.add(
                documents=new_docs,
                metadatas=new_metadatas,
                ids=new_ids
            )
            # Re-load for BM25
            self._load_existing_data()
            print(f"Ingested {len(new_docs)} chunks from {len(files)} files.")
        else:
            print("No new documents found or empty files.")

    def search(self, query: str, top_k: int = 2) -> List[RetrievalResult]:
        results = []
        
        # 1. Semantic Search (Chroma)
        chroma_res = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # 2. Keyword Search (BM25)
        bm25_res_indices = []
        has_bm25_match = False
        
        if self.bm25:
            tokenized_query = query.split(" ")
            bm25_scores = self.bm25.get_scores(tokenized_query)
            # Filter and sort
            # Enumerate scores, filter > 0, sort by score desc
            bm25_hits = [(i, score) for i, score in enumerate(bm25_scores) if score > 0]
            if bm25_hits:
                has_bm25_match = True
            
            bm25_hits.sort(key=lambda x: x[1], reverse=True)
            # Get top_k indices
            bm25_res_indices = [i for i, _ in bm25_hits][:top_k]
        
        # Adaptive Threshold Logic
        # If we found exact keywords (BM25), be lenient with vector distance.
        # If we found NO keywords, be strict (requires strong semantic match).
        if has_bm25_match:
            distance_threshold = 1.6
        else:
            distance_threshold = 1.3 
            
        print(f"Query: '{query}' | BM25 Match: {has_bm25_match} | Threshold: {distance_threshold}")

        seen_content = set()
        
        # Process Chroma results
        if chroma_res['documents'] and chroma_res['distances']:
            for i, doc in enumerate(chroma_res['documents'][0]):
                distance = chroma_res['distances'][0][i]
                
                # Filter out irrelevant documents
                if distance > distance_threshold:
                    print(f"Skipping document (distance {distance:.4f} > {distance_threshold}): {doc[:30]}...")
                    continue
                
                if doc not in seen_content:
                    results.append(RetrievalResult(
                        content=doc,
                        source=chroma_res['metadatas'][0][i]['source'],
                        score=1 - distance, # Normalized somewhat for display, though distance is L2
                        metadata=chroma_res['metadatas'][0][i]
                    ))
                    seen_content.add(doc)

        # Process BM25 results
        for idx in bm25_res_indices:
            doc = self.documents_content[idx]
            if doc not in seen_content:
                meta = self.documents_metadata[idx]
                results.append(RetrievalResult(
                    content=doc,
                    source=meta['source'],
                    score=1.0, # BM25 doesn't give normalized score easily here, treating as high confidence
                    metadata=meta
                ))
                seen_content.add(doc)
        
        return results[:top_k]
