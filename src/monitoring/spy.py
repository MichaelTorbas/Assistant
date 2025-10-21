"""
Monitoring system (spy) for tracking agent operations and memory updates.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class Spy:
    """Monitors and logs all agent operations, memory updates, and conversations."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_log = self.log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

    def log_event(self, event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Log an event to the session log file."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
            "metadata": metadata or {}
        }

        with open(self.session_log, 'a') as f:
            f.write(json.dumps(event, default=str) + '\n')

    def log_message(self, role: str, content: str):
        """Log a conversation message."""
        self.log_event("message", {"role": role, "content": content})

    def log_memory_update(self, update_type: str, details: Dict[str, Any]):
        """Log a memory update operation."""
        self.log_event("memory_update", {"update_type": update_type, "details": details})

    def log_trustcall(self, input_data: Any, output_data: Any, success: bool):
        """Log a TrustCall execution."""
        self.log_event("trustcall", {
            "input": str(input_data),
            "output": str(output_data),
            "success": success
        })

    def log_agent_action(self, action: str, details: Dict[str, Any]):
        """Log an agent action."""
        self.log_event("agent_action", {"action": action, "details": details})

    def log_error(self, error: Exception, context: Optional[str] = None):
        """Log an error."""
        self.log_event("error", {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        })

    def get_session_summary(self) -> str:
        """Generate a summary of the current session."""
        if not self.session_log.exists():
            return "No events logged yet."

        events = []
        with open(self.session_log, 'r') as f:
            for line in f:
                events.append(json.loads(line))

        summary = f"=== SESSION SUMMARY ===\n"
        summary += f"Total events: {len(events)}\n\n"

        event_counts = {}
        for event in events:
            event_type = event['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        summary += "Event breakdown:\n"
        for event_type, count in sorted(event_counts.items()):
            summary += f"  {event_type}: {count}\n"

        return summary

    def tail_logs(self, n: int = 10) -> list:
        """Get the last n log entries."""
        if not self.session_log.exists():
            return []

        with open(self.session_log, 'r') as f:
            lines = f.readlines()
            return [json.loads(line) for line in lines[-n:]]
