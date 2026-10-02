"""Text-to-Speech (TTS) Service using Microsoft Edge Neural Voices."""
import base64
import edge_tts

# Persona Voice Map
PERSONA_VOICES = {
    "Moderator": "en-IN-NeerjaNeural",
    "Analyst": "en-US-AndrewNeural",
    "Contrarian": "en-US-BrianNeural",
    "Peacemaker": "en-US-EmmaNeural",
    "Interviewer": "en-US-GuyNeural",
    "Debater": "en-US-ChristopherNeural"
}

async def generate_neural_audio_b64(text: str, voice: str) -> str:
    """Generates realistic neural speech MP3 audio encoded in Base64 string."""
    try:
        clean_text = text.replace("800M", "800 million").replace("%", " percent")
        communicate = edge_tts.Communicate(clean_text, voice)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        print(f"[TTS Service Warning] Audio generation fallback: {e}")
        return ""
