import streamlit as st
import time
from typing import List
from models import ChatMessage, RetrievalResult
from orchestrator import RAGOrchestrator

# --- Configuration ---
st.set_page_config(
    page_title="Local RAG Chat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Backend ---
@st.cache_resource
def get_orchestrator():
    return RAGOrchestrator()

orchestrator = get_orchestrator()

# --- UI Layout ---
st.title("Local RAG Chat")
st.caption("Powered by Streamlit, LM Studio, and ChromaDB (Local)")

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.info("Ensure LM Studio is running on port 1234.")
    if st.button("Re-Ingest Documents"):
        with st.spinner("Ingesting..."):
            orchestrator.retrieval_system.ingest_documents("./documents")
        st.success("Ingestion Complete!")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Chat Interface ---
# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask me anything about your documents..."):
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Process with Backend
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Call Orchestrator
        # Pass history (excluding current prompt which is already added manually to messages)
        # We need to pass dicts as compatible with orchestrator
        history_for_backend = st.session_state.messages[:-1] 
        
        try:
            stream, sources = orchestrator.query(prompt, history_for_backend)
            
            for chunk in stream:
                full_response += chunk
                response_placeholder.markdown(full_response + "|")
            
            response_placeholder.markdown(full_response)
            
            # Display Sources
            if sources:
                with st.expander("Retrieval Sources", expanded=False):
                    for idx, doc in enumerate(sources):
                        st.markdown(f"**Source {idx+1}:** `{doc.source}`")
                        st.caption(doc.content)
                        st.divider()

        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "I encountered an error. Please check the backend connection."

    # Add Assistant Response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
