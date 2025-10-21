"""
Memory types for the personal assistant agent.
Handles different types of memories: instructions, facts, and todos.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Instruction(BaseModel):
    """System instructions that guide agent behavior."""
    id: str = Field(default_factory=lambda: datetime.now().isoformat())
    content: str
    priority: int = Field(default=1, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Fact(BaseModel):
    """Factual information about the user."""
    id: str = Field(default_factory=lambda: datetime.now().isoformat())
    category: str  # e.g., "preferences", "personal_info", "habits"
    key: str
    value: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    source: Optional[str] = None  # Which conversation it came from


class Todo(BaseModel):
    """User's todo items."""
    id: str = Field(default_factory=lambda: datetime.now().isoformat())
    task: str
    completed: bool = False
    priority: int = Field(default=3, ge=1, le=5)
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)


class MemoryUpdate(BaseModel):
    """Structured output from TrustCall for memory updates."""
    instructions_to_add: List[Instruction] = Field(default_factory=list)
    instructions_to_update: List[Instruction] = Field(default_factory=list)
    instructions_to_remove: List[str] = Field(default_factory=list)  # IDs

    facts_to_add: List[Fact] = Field(default_factory=list)
    facts_to_update: List[Fact] = Field(default_factory=list)
    facts_to_remove: List[str] = Field(default_factory=list)  # IDs

    todos_to_add: List[Todo] = Field(default_factory=list)
    todos_to_update: List[Todo] = Field(default_factory=list)
    todos_to_remove: List[str] = Field(default_factory=list)  # IDs

    reasoning: Optional[str] = None  # Why these changes were made
