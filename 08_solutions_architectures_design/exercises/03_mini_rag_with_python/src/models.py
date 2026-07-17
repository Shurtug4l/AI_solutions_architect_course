from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str
    content: str
    
class RetrievalResult(BaseModel):
    content: str
    source: str = "unknown"
    score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
