import msvcrt
import sys
import re
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from config import CYAN, GREEN, CONVERSATIONS_DIR

console = Console()

def read_single_keypress():
    while True:
        try:
            key = msvcrt.getch().decode('utf-8').lower()
            if key in ['\r', 'r', 'o', '\x03']:  # Enter key, 'r', 'o', or Ctrl+C
                return key
        except KeyboardInterrupt:
            print("\nExiting the simulation...")
            sys.exit(0)

def print_separator():
    console.print("=" * 120, style="dim")

def print_thinking_animation(claude_number, stop_event):
    color = CYAN if claude_number == 1 else GREEN
    with console.status(f"[{color}]Agent #{claude_number} is thinking...", spinner="dots") as status:
        while not stop_event.is_set():
            pass

def escape_chars(text):
    return re.sub(r'\\n', '\n', text)

def ensure_conversations_directory():
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

def get_full_path(file_path):
    if not os.path.isabs(file_path):
        if os.path.exists(file_path):
            return file_path
        full_path = os.path.join(CONVERSATIONS_DIR, file_path)
    else:
        full_path = file_path

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"No such file or directory: '{full_path}'")
    return full_path

def get_user_input(prompt):
    console.print(f"[yellow]{prompt}[/yellow]", end="")
    return input()
