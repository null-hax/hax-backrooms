import anthropic
import requests
from config import MODEL, MAX_TOKENS, VOICE_IDS, SYSTEM_MESSAGE_1, SYSTEM_MESSAGE_2
from secrets import ANTHROPIC_API_KEY, ELEVEN_LABS_API_KEY
from text_processing import preprocess_for_tts

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_claude_response(claude_num, conversation):
    # Use appropriate system message based on claude_num
    system_message = SYSTEM_MESSAGE_1 if claude_num == 1 else SYSTEM_MESSAGE_2

    return anthropic_client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_message,
        messages=conversation
    )

def text_to_speech(text, claude_num):
    # Temporarily disable text-to-speech for Agent 2
    if claude_num == 2:
        return None

    preprocessed_text = preprocess_for_tts(text, is_agent_2=(claude_num == 2))
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_IDS[claude_num]}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }

    data = {
        "text": preprocessed_text[:5000],  # Limit text to 5000 characters
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.content
