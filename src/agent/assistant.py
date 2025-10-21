"""
Main personal assistant agent with multi-memory system.
"""

from typing import List, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from src.memory import MemoryStore
from src.monitoring import Spy
from .memory_processor import MemoryProcessor


class PersonalAssistant:
    """
    LangChain-based personal assistant with multi-memory capabilities.

    Features:
    - Maintains instructions, facts, and todos
    - Uses TrustCall for memory extraction
    - Monitors all operations with spy()
    - Stores everything locally
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model

        # Initialize components
        self.memory_store = MemoryStore()
        self.spy = Spy()
        self.memory_processor = MemoryProcessor(api_key, self.spy, model)
        self.llm = ChatAnthropic(api_key=api_key, model=model)

        # Conversation history
        self.conversation_history: List[BaseMessage] = []

        self.spy.log_agent_action("initialized", {
            "model": model,
            "memory_store": "ready",
            "spy": "active"
        })

    def _build_system_message(self) -> str:
        """Build the system message with current memory context."""
        context = self.memory_store.get_context_summary()

        system_msg = f"""You are a helpful personal assistant with memory capabilities.

{context}

Your role:
1. Help the user with questions and tasks
2. Remember information about the user (this happens automatically)
3. Track and manage their todos
4. Follow the instructions provided above
5. Be conversational and helpful

When the user shares information about themselves, their preferences, or asks you to remember something,
acknowledge it naturally. The system will automatically extract and store this information.

When discussing todos, be specific and actionable.
"""
        return system_msg

    def chat(self, user_message: str, auto_extract_memories: bool = True) -> str:
        """
        Process a user message and return a response.

        Args:
            user_message: The user's input
            auto_extract_memories: Whether to automatically extract memories from the conversation

        Returns:
            The assistant's response
        """
        self.spy.log_message("user", user_message)

        # Build messages
        messages = [SystemMessage(content=self._build_system_message())]
        messages.extend(self.conversation_history)
        messages.append(HumanMessage(content=user_message))

        try:
            # Get response from LLM
            response = self.llm.invoke(messages)
            assistant_message = response.content

            self.spy.log_message("assistant", assistant_message)

            # Update conversation history
            self.conversation_history.append(HumanMessage(content=user_message))
            self.conversation_history.append(AIMessage(content=assistant_message))

            # Auto-extract memories if enabled
            if auto_extract_memories:
                self._extract_and_update_memories(user_message, assistant_message)

            return assistant_message

        except Exception as e:
            self.spy.log_error(e, context="PersonalAssistant.chat")
            return f"I encountered an error: {str(e)}"

    def _extract_and_update_memories(self, user_message: str, assistant_response: str):
        """Extract memories from the conversation and update storage."""
        current_context = self.memory_store.get_context_summary()

        memory_update = self.memory_processor.quick_extract(
            user_message,
            assistant_response,
            current_context
        )

        if memory_update and memory_update.reasoning:
            # Check if there are actual updates
            has_updates = (
                memory_update.instructions_to_add or
                memory_update.facts_to_add or
                memory_update.todos_to_add or
                memory_update.instructions_to_update or
                memory_update.facts_to_update or
                memory_update.todos_to_update or
                memory_update.instructions_to_remove or
                memory_update.facts_to_remove or
                memory_update.todos_to_remove
            )

            if has_updates:
                self.spy.log_memory_update("auto_extract", {
                    "reasoning": memory_update.reasoning,
                    "updates": memory_update.model_dump()
                })

                self.memory_store.apply_memory_update(memory_update)

    def get_todos(self, include_completed: bool = False) -> List:
        """Get user's todos."""
        return self.memory_store.get_todos(include_completed)

    def get_facts(self, category: Optional[str] = None) -> List:
        """Get facts about the user."""
        return self.memory_store.get_facts(category)

    def get_instructions(self) -> List:
        """Get system instructions."""
        return self.memory_store.get_instructions()

    def clear_conversation(self):
        """Clear conversation history (but keep memories)."""
        self.conversation_history = []
        self.spy.log_agent_action("conversation_cleared", {})

    def get_session_summary(self) -> str:
        """Get a summary of the current session."""
        return self.spy.get_session_summary()
