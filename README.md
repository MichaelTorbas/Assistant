# Personal Assistant - Multi-Memory AI Chatbot

Learning to fly in AI

A LangChain-based personal assistant with multi-memory capabilities, powered by Claude (Anthropic). This assistant remembers facts about you, tracks your todos, follows custom instructions, and stores everything locally on your machine.

## Features

- **Multi-Memory System**
  - 📝 **Instructions**: System-level directives that guide the assistant's behavior
  - 📚 **Facts**: Factual information about you (preferences, personal info, habits, etc.)
  - ✅ **Todos**: Your task list with priorities and completion tracking

- **TrustCall Integration**: Uses Claude's structured output for reliable memory extraction
- **Spy Monitoring**: Comprehensive logging of all operations and memory updates
- **Local Storage**: All memories stored in JSON files on your machine
- **Auto-Memory Extraction**: Automatically extracts and updates memories from conversations

## Architecture

```
src/
├── memory/           # Memory system (types, storage)
├── agent/            # LangChain agent and memory processor
└── monitoring/       # Spy logging system

memories/             # Local JSON storage (created on first run)
├── instructions.json
├── facts.json
└── todos.json

logs/                 # Session logs (created on first run)
└── session_*.jsonl
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Run the Assistant

```bash
python main.py
```

## Usage

### Basic Chat

Just type naturally and the assistant will respond while automatically extracting and storing memories:

```
You: Hi! I'm John and I live in San Francisco.
Assistant: Hello John! Nice to meet you...

You: I prefer Python over JavaScript for backend work.
Assistant: Got it! I'll keep that in mind...
```

### Commands

- `/todos` - View your todo list
- `/facts` - View all stored facts about you
- `/instructions` - View system instructions
- `/summary` - View session statistics
- `/clear` - Clear conversation history (keeps memories)
- `/quit` or `/exit` - Exit the program

### Examples

**Adding Todos:**
```
You: Remind me to buy groceries tomorrow and finish the project report by Friday.
Assistant: I'll help you track those tasks...
```

**Setting Preferences:**
```
You: I prefer concise responses and always use metric units.
Assistant: Understood! I'll keep my responses concise and use metric units...
```

**Asking Questions:**
```
You: What do you know about my preferences?
Assistant: Based on what you've told me...
```

## How It Works

1. **Memory Extraction**: After each conversation, the system uses Claude with structured output (TrustCall) to extract:
   - New facts about you
   - Todo items
   - Behavioral instructions

2. **Local Storage**: All memories are stored in `memories/` as JSON files:
   - `instructions.json` - How the assistant should behave
   - `facts.json` - Information about you
   - `todos.json` - Your task list

3. **Context Building**: Each message includes current memories in the system prompt, so the assistant always has access to everything it knows about you

4. **Monitoring**: The `spy()` system logs all operations to `logs/` for debugging and analysis

## Memory Types

### Instructions
- Priority-based (1-10)
- Guide assistant behavior
- Example: "Always be concise", "Use metric units"

### Facts
- Categorized information about you
- Categories: preferences, personal_info, habits, work, hobbies, etc.
- Example: "User prefers dark mode", "User is a software engineer"

### Todos
- Priority-based (1-5)
- Track completion status
- Optional due dates and tags
- Example: "Buy groceries [Priority 3]"

## Development

### Project Structure

- `src/memory/` - Memory types and storage system
  - `memory_types.py` - Pydantic models for Instructions, Facts, Todos
  - `memory_store.py` - JSON-based persistence layer

- `src/agent/` - Agent implementation
  - `assistant.py` - Main PersonalAssistant class
  - `memory_processor.py` - TrustCall-based memory extraction

- `src/monitoring/` - Logging and monitoring
  - `spy.py` - Event logging system

### Extending the System

**Add a new memory type:**
1. Define model in `src/memory/memory_types.py`
2. Add storage methods in `src/memory/memory_store.py`
3. Update `MemoryUpdate` model
4. Update memory processor prompt

**Customize extraction:**
Edit the system prompt in `src/agent/memory_processor.py`

## Requirements

- Python 3.8+
- Anthropic API key
- Dependencies listed in `requirements.txt`

## Privacy & Security

- All data stored locally on your machine
- No data sent anywhere except to Anthropic's API for processing
- API key stored in `.env` (not committed to git)
- Memories stored in plain JSON (human-readable)

## License

MIT License - Feel free to modify and use as you like!
