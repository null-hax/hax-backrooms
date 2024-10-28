import tempfile
import os
import pygame

pygame.mixer.init()

def save_audio_to_temp_file(audio_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        temp_file.write(audio_content)
        return temp_file.name

def play_audio(audio_file):
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Clean up the temporary file
    pygame.mixer.music.unload()
    os.remove(audio_file)
