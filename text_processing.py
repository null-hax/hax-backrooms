import re
from nltk.tokenize import sent_tokenize
from config import WPM
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
import time
import random

def preprocess_for_tts(text, is_agent_2=False):
    if not is_agent_2:
        return preprocess_agent1(text)
    else:
        return preprocess_agent2(text)

def preprocess_agent1(text):
    replacements = {
        '$': 'dollar sign ',
        '#': 'hash ',
        '~': 'tilde ',
        '|': 'pipe ',
        '>': 'greater than ',
        '<': 'less than ',
        '&': 'ampersand ',
        '^': 'caret ',
        '*': 'asterisk ',
        '\\': 'backslash ',
        '/': 'forward slash ',
        '`': 'backtick ',
        'ls': 'list: ',
        'cd': 'change directory: ',
        'mkdir': 'make directory: ',
        'rm': 'remove: ',
        'mv': 'move: ',
        'cp': 'copy: ',
        'sudo': 'super user do: ',
        'grep': 'global regular expression print: ',
        'chmod': 'change mode: ',
        'chown': 'change owner: ',
        'ssh': 'secure shell: ',
        'scp': 'secure copy: ',
        'apt-get': 'apt get: ',
        'git': 'git: ',
        'cat': 'concatenate and display: ',
        'pwd': 'print working directory: ',
        'whoami': 'who am i: ',
        'uname': 'unix name: ',
    }

    lines = text.split('\n')
    processed_lines = []
    ascii_art_buffer = []

    for line in lines:
        if re.match(r'^[\s\W]+$', line) or (len(ascii_art_buffer) > 0 and len(line.strip()) < 10):
            ascii_art_buffer.append(line)
        else:
            if ascii_art_buffer:
                processed_lines.append("ASCII art: visual representation.")
                ascii_art_buffer = []
            
            for key, value in replacements.items():
                line = re.sub(r'\b' + re.escape(key) + r'\b', value, line)

            line = re.sub(r'([-drwx]{10})\s+(\d+)\s+(\w+)\s+(\w+)\s+(\d+)', 
                          lambda m: f"File permissions {m.group(1)}, size {m.group(5)} bytes.", line)
            line = re.sub(r'([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2})', 
                          lambda m: f"Date {m.group(1)}.", line)
            line = re.sub(r'([a-zA-Z_][a-zA-Z0-9_-]*\.[a-zA-Z0-9]+)', r'\1', line)
            line = re.sub(r'(\w+)@(\w+):([~\w/]*)[#$]', lambda m: f"{m.group(1)} at {m.group(2)}, path {m.group(3)}: ", line)
            line = re.sub(r'(\w+)/$', r'\1,', line)

            processed_lines.append(line)

    if ascii_art_buffer:
        processed_lines.append("ASCII art: visual representation.")

    processed_text = ' '.join(processed_lines)
    processed_text = re.sub(r'[_]+', ' ', processed_text)
    processed_text = ''.join(char if char.isascii() and char.isprintable() else ' ' for char in processed_text)
    processed_text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', processed_text)
    processed_text = re.sub(r'([a-z])\s+([A-Z])', r'\1. \2', processed_text)

    return processed_text.strip()

def preprocess_agent2(text):
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        if re.match(r'^[\s\W]+$', line) or re.match(r'\w+@\w+:.*[$#]', line):
            continue
        
        line = re.sub(r'[-drwx]{10}\s+\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\d+\s+\d+:\d+', '', line)
        line = line.replace('_', ' ')
        
        words = line.split()
        meaningful_words = [word for word in words if len(word) > 1 and not word.startswith('-')]
        
        if meaningful_words:
            processed_lines.append(' '.join(meaningful_words))
    
    processed_text = ' '.join(processed_lines)
    processed_text = re.sub(r'[^\w\s.,?!-]', ' ', processed_text)
    
    sentences = sent_tokenize(processed_text)
    simplified_sentences = []
    for sentence in sentences:
        if len(sentence.split()) > 3 and not sentence.startswith(("ASCII art", "File permissions", "Date", "hidden file", "file")):
            sentence = sentence.capitalize()
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            simplified_sentences.append(sentence)
    
    simplified_text = ' '.join(simplified_sentences)
    final_text = ' '.join(simplified_text.split()[:50])
    
    return final_text.strip()

def simulate_typing(lines, title, color, wpm=WPM):
    with Live(refresh_per_second=20) as live:
        typed_lines = []
        for line in lines:
            current_line = ""
            for char in line:
                current_line += char
                panel = Panel(Text('\n'.join(typed_lines + [current_line])), title=title, border_style=color, width=120)
                live.update(panel)
                time.sleep(1/wpm + random.uniform(0, 0.01))
            typed_lines.append(current_line)
        
        final_panel = Panel(Text('\n'.join(typed_lines)), title=title, border_style=color, width=120)
        live.update(final_panel)
        time.sleep(0.5)
