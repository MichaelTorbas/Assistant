"""
Local file-based memory storage system.
Persists all memories to disk in JSON format.
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from .memory_types import Instruction, Fact, Todo, MemoryUpdate


class MemoryStore:
    """Manages persistent storage of memories on local disk."""

    def __init__(self, storage_dir: str = "memories"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.instructions_file = self.storage_dir / "instructions.json"
        self.facts_file = self.storage_dir / "facts.json"
        self.todos_file = self.storage_dir / "todos.json"

        # Initialize files if they don't exist
        self._initialize_storage()

    def _initialize_storage(self):
        """Create storage files with default content if they don't exist."""
        default_instruction = Instruction(
            content="You are a helpful personal assistant. Remember information about the user and help them stay organized.",
            priority=10
        )

        if not self.instructions_file.exists():
            self._save_json(self.instructions_file, [default_instruction.model_dump(mode='json')])

        if not self.facts_file.exists():
            self._save_json(self.facts_file, [])

        if not self.todos_file.exists():
            self._save_json(self.todos_file, [])

    def _save_json(self, file_path: Path, data: Any):
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _load_json(self, file_path: Path) -> Any:
        """Load data from JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    # Instructions
    def get_instructions(self) -> List[Instruction]:
        """Retrieve all instructions, sorted by priority (highest first)."""
        data = self._load_json(self.instructions_file)
        instructions = [Instruction(**item) for item in data]
        return sorted(instructions, key=lambda x: x.priority, reverse=True)

    def add_instruction(self, instruction: Instruction):
        """Add a new instruction."""
        instructions = self._load_json(self.instructions_file)
        instructions.append(instruction.model_dump(mode='json'))
        self._save_json(self.instructions_file, instructions)

    def update_instruction(self, instruction: Instruction):
        """Update existing instruction by ID."""
        instructions = self._load_json(self.instructions_file)
        for i, item in enumerate(instructions):
            if item['id'] == instruction.id:
                instructions[i] = instruction.model_dump(mode='json')
                break
        self._save_json(self.instructions_file, instructions)

    def remove_instruction(self, instruction_id: str):
        """Remove instruction by ID."""
        instructions = self._load_json(self.instructions_file)
        instructions = [item for item in instructions if item['id'] != instruction_id]
        self._save_json(self.instructions_file, instructions)

    # Facts
    def get_facts(self, category: Optional[str] = None) -> List[Fact]:
        """Retrieve all facts, optionally filtered by category."""
        data = self._load_json(self.facts_file)
        facts = [Fact(**item) for item in data]
        if category:
            facts = [f for f in facts if f.category == category]
        return sorted(facts, key=lambda x: x.updated_at, reverse=True)

    def add_fact(self, fact: Fact):
        """Add a new fact."""
        facts = self._load_json(self.facts_file)
        facts.append(fact.model_dump(mode='json'))
        self._save_json(self.facts_file, facts)

    def update_fact(self, fact: Fact):
        """Update existing fact by ID."""
        facts = self._load_json(self.facts_file)
        for i, item in enumerate(facts):
            if item['id'] == fact.id:
                facts[i] = fact.model_dump(mode='json')
                break
        self._save_json(self.facts_file, facts)

    def remove_fact(self, fact_id: str):
        """Remove fact by ID."""
        facts = self._load_json(self.facts_file)
        facts = [item for item in facts if item['id'] != fact_id]
        self._save_json(self.facts_file, facts)

    # Todos
    def get_todos(self, include_completed: bool = False) -> List[Todo]:
        """Retrieve todos, optionally including completed ones."""
        data = self._load_json(self.todos_file)
        todos = [Todo(**item) for item in data]
        if not include_completed:
            todos = [t for t in todos if not t.completed]
        return sorted(todos, key=lambda x: (x.completed, -x.priority, x.created_at))

    def add_todo(self, todo: Todo):
        """Add a new todo."""
        todos = self._load_json(self.todos_file)
        todos.append(todo.model_dump(mode='json'))
        self._save_json(self.todos_file, todos)

    def update_todo(self, todo: Todo):
        """Update existing todo by ID."""
        todos = self._load_json(self.todos_file)
        for i, item in enumerate(todos):
            if item['id'] == todo.id:
                todos[i] = todo.model_dump(mode='json')
                break
        self._save_json(self.todos_file, todos)

    def remove_todo(self, todo_id: str):
        """Remove todo by ID."""
        todos = self._load_json(self.todos_file)
        todos = [item for item in todos if item['id'] != todo_id]
        self._save_json(self.todos_file, todos)

    def apply_memory_update(self, update: MemoryUpdate):
        """Apply a batch memory update from TrustCall."""
        # Instructions
        for instruction in update.instructions_to_add:
            self.add_instruction(instruction)
        for instruction in update.instructions_to_update:
            self.update_instruction(instruction)
        for instruction_id in update.instructions_to_remove:
            self.remove_instruction(instruction_id)

        # Facts
        for fact in update.facts_to_add:
            self.add_fact(fact)
        for fact in update.facts_to_update:
            self.update_fact(fact)
        for fact_id in update.facts_to_remove:
            self.remove_fact(fact_id)

        # Todos
        for todo in update.todos_to_add:
            self.add_todo(todo)
        for todo in update.todos_to_update:
            self.update_todo(todo)
        for todo_id in update.todos_to_remove:
            self.remove_todo(todo_id)

    def get_context_summary(self) -> str:
        """Generate a summary of all memories for agent context."""
        instructions = self.get_instructions()
        facts = self.get_facts()
        todos = self.get_todos()

        summary = "=== AGENT INSTRUCTIONS ===\n"
        for inst in instructions:
            summary += f"[Priority {inst.priority}] {inst.content}\n"

        summary += "\n=== USER FACTS ===\n"
        for fact in facts:
            summary += f"[{fact.category}] {fact.key}: {fact.value}\n"

        summary += "\n=== USER TODOS ===\n"
        for todo in todos:
            status = "✓" if todo.completed else "○"
            summary += f"{status} [P{todo.priority}] {todo.task}\n"

        return summary
