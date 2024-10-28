import argparse
import sys
import os
import json
# Hide Pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from conversation_manager import ConversationManager
from config import INITIAL_CONVERSATION, SEED_MESSAGES
from cli_utils import console, ensure_conversations_directory, get_full_path

# Initialize pygame mixer for audio playback
pygame.mixer.init()

def parse_arguments():
    """Parse command line arguments for simulation configuration"""
    parser = argparse.ArgumentParser(description="Run the simulation.")
    # Enable supervised mode for manual control of responses
    parser.add_argument('-s', '--supervised', action='store_true', help='Run in supervised mode')
    # Set number of back-and-forth exchanges between Claudes
    parser.add_argument('-n', '--exchanges', type=int, default=5, help='Number of exchanges to run')
    # Load previous conversation from file
    parser.add_argument('-i', '--input-file', type=str, help='Path to the input conversation file')
    # Enable text-to-speech for Agent #1
    parser.add_argument('-v', '--voice', action='store_true', help='Enable text-to-speech functionality')
    # Set initial topic for conversation
    parser.add_argument('-t', '--topic', type=str, help='Seed topic for the conversation')
    return parser.parse_args()

def load_conversation(file_path):
    """Load and parse a previous conversation file"""
    full_path = get_full_path(file_path)
    conversation_1, conversation_2 = [], []

    try:
        # First attempt: Try to load the entire file as JSON
        with open(full_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Process each message and distribute to appropriate conversation
            for message in data:
                if message['role'] == 'user':
                    conversation_1.append(message)
                elif message['role'] == 'assistant':
                    # Assistant messages go to Claude1's history
                    conversation_1.append(message)
                    # And become user input for Claude2
                    conversation_2.append({"role": "user", "content": message['content']})
    except json.JSONDecodeError as e:
        # Fallback: Try to read file line by line if full JSON parse fails
        print(f"Error decoding JSON in file {full_path}: {str(e)}")
        print("Attempting to read file line by line...")
        with open(full_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    message = json.loads(line.strip())
                    if message['role'] == 'user':
                        conversation_1.append(message)
                    elif message['role'] == 'assistant':
                        conversation_1.append(message)
                        conversation_2.append({"role": "user", "content": message['content']})
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line.strip()}")

    return conversation_1, conversation_2

def main():
    """Main function to run the Claude Backrooms simulation"""
    # Create conversations directory if it doesn't exist
    ensure_conversations_directory()
    args = parse_arguments()
    console.print(f"[blue]Starting the simulation...[/]")

    # Load conversation history if input file provided
    if args.input_file:
        try:
            conversation_1, conversation_2 = load_conversation(args.input_file)
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            print("Please make sure the file exists and the path is correct.")
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred while loading the conversation: {str(e)}")
            sys.exit(1)
    else:
        # Start fresh conversation with initial setup
        conversation_1 = INITIAL_CONVERSATION
        conversation_2 = []

    # Add seed message based on topic if provided
    if args.topic:
        seed_message = SEED_MESSAGES["with_topic"].format(topic=args.topic)
        # Add as Claude1's response
        conversation_1.append({"role": "assistant", "content": seed_message})
        # Add as user input for Claude2
        conversation_2.append({"role": "user", "content": seed_message})
    else:
        # Use default seed message if no topic
        seed_message = SEED_MESSAGES["default"]
        conversation_1.append({"role": "assistant", "content": seed_message})
        conversation_2.append({"role": "user", "content": seed_message})
    
    # Initialize conversation manager with settings
    manager = ConversationManager(
        conversation_1, 
        conversation_2, 
        num_exchanges=args.exchanges, 
        supervised_mode=args.supervised, 
        voice_enabled=args.voice
    )
    
    # Set seed message if topic provided
    if args.topic:
        manager.set_seed_message(seed_message)
    
    # Start the conversation loop
    manager.run()

if __name__ == "__main__":
    main()
