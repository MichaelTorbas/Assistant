"""
TrustCall-based memory processor.
Extracts structured memory updates from conversations.
"""

from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.memory import MemoryUpdate, Instruction, Fact, Todo
from src.monitoring import Spy
import json


class MemoryProcessor:
    """Uses TrustCall to extract and structure memory updates from conversations."""

    def __init__(self, api_key: str, spy: Spy, model: str = "claude-3-5-sonnet-20241022"):
        self.llm = ChatAnthropic(
            api_key=api_key,
            model=model,
            temperature=0
        )
        self.spy = spy

    def extract_memory_updates(self, conversation: str, current_context: str) -> Optional[MemoryUpdate]:
        """
        Analyze conversation and extract memory updates using structured output (TrustCall).

        Args:
            conversation: The recent conversation text
            current_context: Current memory state for reference

        Returns:
            MemoryUpdate object with all changes to make, or None if no updates needed
        """
        system_prompt = """You are a memory extraction system. Your job is to analyze conversations and extract:

1. INSTRUCTIONS: System-level directives about how the assistant should behave
   - Example: "Always be concise", "Prefer Python over JavaScript", "Use metric units"

2. FACTS: Factual information about the user
   - Categories: preferences, personal_info, habits, work, hobbies, relationships, etc.
   - Example: "User prefers dark mode", "User lives in San Francisco", "User is a software engineer"

3. TODOS: Action items the user wants to track
   - Example: "Buy groceries", "Finish project report", "Call mom"

CURRENT MEMORY STATE:
{current_context}

Analyze the conversation and extract any NEW information or UPDATES to existing information.
Return a structured JSON object with the updates.

For facts, assign appropriate categories. For priorities:
- Instructions: 1-10 (10 = highest)
- Todos: 1-5 (5 = highest)

Include a 'reasoning' field explaining why you made these changes."""

        user_prompt = f"""Analyze this conversation and extract memory updates:

{conversation}

Return JSON with this structure:
{{
  "instructions_to_add": [...],
  "facts_to_add": [...],
  "todos_to_add": [...],
  "reasoning": "..."
}}

Only include fields that have updates. If nothing to extract, return {{"reasoning": "No memory updates needed"}}.
"""

        try:
            messages = [
                SystemMessage(content=system_prompt.format(current_context=current_context)),
                HumanMessage(content=user_prompt)
            ]

            # Use TrustCall via structured output
            structured_llm = self.llm.with_structured_output(MemoryUpdate)
            result = structured_llm.invoke(messages)

            self.spy.log_trustcall(
                input_data={"conversation": conversation[:200] + "..."},
                output_data=result.model_dump() if result else None,
                success=True
            )

            return result

        except Exception as e:
            self.spy.log_error(e, context="MemoryProcessor.extract_memory_updates")
            return None

    def quick_extract(self, user_message: str, assistant_response: str, current_context: str) -> Optional[MemoryUpdate]:
        """
        Quick extraction from a single exchange.

        Args:
            user_message: What the user said
            assistant_response: How the assistant responded
            current_context: Current memory state

        Returns:
            MemoryUpdate or None
        """
        conversation = f"User: {user_message}\nAssistant: {assistant_response}"
        return self.extract_memory_updates(conversation, current_context)
