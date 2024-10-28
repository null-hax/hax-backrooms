import threading
from datetime import datetime
import os
import sys
import json
from config import CONVERSATIONS_DIR, CYAN, GREEN, ORANGE, PURPLE, RED
from api_client import get_claude_response, text_to_speech
from text_processing import simulate_typing, preprocess_for_tts
from audio_handler import save_audio_to_temp_file, play_audio
from cli_utils import console, read_single_keypress, print_separator, print_thinking_animation, escape_chars, get_user_input

class ConversationManager:
    def __init__(self, conversation_1, conversation_2, num_exchanges=5, supervised_mode=True, voice_enabled=False):
        self.conversation_1 = conversation_1
        self.conversation_2 = conversation_2
        self.num_exchanges = num_exchanges
        self.supervised_mode = supervised_mode
        self.voice_enabled = voice_enabled
        self.filename = os.path.join(CONVERSATIONS_DIR, f"conversation_{int(datetime.now().timestamp())}.json")
        self.seed_message = None

    def run(self):
        try:
            # Ensure the CONVERSATIONS_DIR exists
            os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
            
            # Create the file if it doesn't exist
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump([], file)

            with open(self.filename, "r+", encoding="utf-8") as file:
                self._write_initial_conversation(file)
                for _ in range(self.num_exchanges):
                    self._conduct_exchange(file)
        except IOError as e:
            print(f"An I/O error occurred: {str(e)}")
            print("Please check if you have the necessary permissions to read/write in the specified directory.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nExiting the simulation...")
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            sys.exit(1)

    def _write_initial_conversation(self, file):
        file.seek(0)
        json.dump(self.conversation_1, file, ensure_ascii=False, indent=2)
        file.write('\n')  # Add a newline at the end of the file
        file.truncate()
        file.flush()

    def _conduct_exchange(self, file):
        for claude_num, conversation in [(1, self.conversation_1), (2, self.conversation_2)]:
            while True:
                response = self._get_claude_response(claude_num, conversation)
                if response and response.content:
                    formatted_response = self._escape_chars(response.content[0].text)
                    
                    if claude_num == 1 and self.seed_message:
                        formatted_response = f"{self.seed_message}{formatted_response}"
                        self.seed_message = None  # Clear the seed message after using it
                    
                    self._display_response(claude_num, formatted_response)
                    
                    action, message = self._handle_user_input(claude_num, formatted_response, file)
                    if action == "continue":
                        self._update_conversations(claude_num, message)
                        break
                    elif action == "override":
                        self._update_conversations(claude_num, message)
                        break
                    # If action is "retry", the loop will continue
                else:
                    console.print(f"[red]Error: Received an empty response from Claude {claude_num}[/]")
                    if self.supervised_mode:
                        console.print(f"[{ORANGE}]Press [green]Enter[/green] to retry, or [red]Ctrl+C[/red] to exit.[/]")
                        key = read_single_keypress()
                        if key == '\r':  # Enter key
                            continue
                        elif key == '\x03':  # Ctrl+C
                            raise KeyboardInterrupt
                    else:
                        break

    def _display_thinking(self, claude_num):
        color = CYAN if claude_num == 1 else GREEN
        message = f"Agent #{claude_num} is thinking..."
        print_thinking_animation(claude_num, threading.Event())

    def _get_claude_response(self, claude_num, conversation):
        stop_event = threading.Event()
        thinking_thread = threading.Thread(target=print_thinking_animation, args=(claude_num, stop_event))
        thinking_thread.start()

        try:
            return get_claude_response(claude_num, conversation)
        finally:
            stop_event.set()
            thinking_thread.join()

    def _display_response(self, claude_num, formatted_response):
        color = CYAN if claude_num == 1 else GREEN
        title = f"Agent #{claude_num}"
        
        if self.voice_enabled and claude_num == 1:
            preprocessed_text = preprocess_for_tts(formatted_response, is_agent_2=(claude_num == 2))
            audio_content = text_to_speech(preprocessed_text, claude_num)
            
            if audio_content:
                audio_file = save_audio_to_temp_file(audio_content)
                threading.Thread(target=play_audio, args=(audio_file,)).start()
        
        # Remove leading and trailing whitespace, including newlines
        formatted_response = formatted_response.strip()
        
        # Split the response into lines, preserving intentional newlines
        lines = formatted_response.split('\n')
        
        # Remove any empty lines at the beginning or end of the list
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        simulate_typing(lines, title, color)

    def _handle_user_input(self, claude_num, formatted_response, file):
        if self.supervised_mode:
            console.print(f"[{ORANGE}]Press [green]Enter[/green] to continue, [cyan]'R'[/cyan] to retry, [purple]'O'[/purple] to override, or [red]Ctrl+C[/red] to exit.[/]")
            key = read_single_keypress()
            if key == '\r':  # Enter key
                self._write_response_to_file(claude_num, formatted_response, file)
                return "continue", formatted_response
            elif key == 'r':  # Retry
                console.print(f"[{PURPLE}]Retrying...[/]")
                return "retry", None
            elif key == 'o':  # Override
                override_message = get_user_input("Enter your override message: ")
                self._write_response_to_file(claude_num, override_message, file)
                return "override", override_message
            elif key == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
        else:
            self._write_response_to_file(claude_num, formatted_response, file)
            return "continue", formatted_response

    def _update_conversations(self, claude_num, formatted_response):
        if claude_num == 1:
            self.conversation_1.append({"role": "assistant", "content": formatted_response})
            self.conversation_2.append({"role": "user", "content": formatted_response})
        else:
            self.conversation_1.append({"role": "user", "content": formatted_response})
            self.conversation_2.append({"role": "assistant", "content": formatted_response})

    def _write_response_to_file(self, claude_num, formatted_response, file):
        role = "assistant" if claude_num == 1 else "user"
        new_message = {"role": role, "content": formatted_response}
        
        # Read existing content
        file.seek(0)
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []
        
        # Append new message
        data.append(new_message)
        
        # Write updated content
        file.seek(0)
        file.truncate()
        json.dump(data, file, ensure_ascii=False, indent=2, separators=(',', ': '))
        file.write('\n')  # Add a newline at the end of the file
        file.flush()

    def _escape_chars(self, text):
        return escape_chars(text)
    def set_seed_message(self, message):
        self.seed_message = message

