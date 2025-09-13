from typing import List, Dict, Any
from pydantic import BaseModel, Field

class Memory(BaseModel):
    roles_needed: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    clarifying_questions: List[str] = Field(default_factory=list)
    job_descriptions: List[Dict[str, Any]] = Field(default_factory=list)
    hiring_plan: Dict[str, Any] = Field(default_factory=dict)
    tools_used: List[str] = Field(default_factory=list)
