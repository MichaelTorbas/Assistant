"""
Main entry point for the Personal Assistant chatbot.
"""

import os
from dotenv import load_dotenv
from src.agent import PersonalAssistant


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*60)
    print("  PERSONAL ASSISTANT - Multi-Memory AI Chatbot")
    print("="*60)
    print("\nCommands:")
    print("  /todos         - View your todo list")
    print("  /facts         - View facts about you")
    print("  /instructions  - View system instructions")
    print("  /summary       - View session summary")
    print("  /clear         - Clear conversation history")
    print("  /quit or /exit - Exit the program")
    print("\n" + "="*60 + "\n")


def main():
    """Main chat loop."""
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key:")
        print("ANTHROPIC_API_KEY=your_key_here")
        return

    # Initialize assistant
    print("Initializing Personal Assistant...")
    assistant = PersonalAssistant(api_key)

    print_banner()

    # Main chat loop
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['/quit', '/exit']:
                print("\nGoodbye! Your memories have been saved.")
                break

            elif user_input.lower() == '/todos':
                todos = assistant.get_todos()
                if todos:
                    print("\n📋 Your Todos:")
                    for todo in todos:
                        status = "✓" if todo.completed else "○"
                        print(f"  {status} [P{todo.priority}] {todo.task}")
                else:
                    print("\n📋 No todos yet!")
                print()
                continue

            elif user_input.lower() == '/facts':
                facts = assistant.get_facts()
                if facts:
                    print("\n📚 Facts About You:")
                    current_category = None
                    for fact in facts:
                        if fact.category != current_category:
                            current_category = fact.category
                            print(f"\n  [{fact.category.upper()}]")
                        print(f"    • {fact.key}: {fact.value}")
                else:
                    print("\n📚 No facts stored yet!")
                print()
                continue

            elif user_input.lower() == '/instructions':
                instructions = assistant.get_instructions()
                print("\n⚙️  System Instructions:")
                for inst in instructions:
                    print(f"  [Priority {inst.priority}] {inst.content}")
                print()
                continue

            elif user_input.lower() == '/summary':
                summary = assistant.get_session_summary()
                print(f"\n{summary}\n")
                continue

            elif user_input.lower() == '/clear':
                assistant.clear_conversation()
                print("\n🔄 Conversation history cleared (memories preserved)\n")
                continue

            # Regular chat
            response = assistant.chat(user_input)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye! Your memories have been saved.")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    main()
