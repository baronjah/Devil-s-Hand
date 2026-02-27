import os
import json
import re
import urllib.request
from datetime import datetime

class BasketRouter:
    """
    The "Professional Receptionist" for Devil's Hand.
    Takes messy human prompts and extracts structured intent.
    """
    def __init__(self, ollama_url="http://localhost:11434/api/generate"):
        self.ollama_url = ollama_url
        self.model = "gemma" # Using the instruction-tuned model from Claude's logs

    def route_prompt(self, raw_text):
        print(f"BasketRouter: 📥 Ingesting prompt: {raw_text[:50]}...")
        
        system_prompt = """
        You are the 'Ancient Screenwriter' receptionist for the Devil's Hand ecosystem.
        Your job is to take messy, lowercase, comma-separated human thoughts and extract structured intents.
        
        Rules:
        1. Identify the 'CORE_INTENT' (e.g., CREATE_STORY, MODIFY_CODE, EXECUTE_JUDGEMENT, SYSTEM_QUERY).
        2. Extract 'ACTORS' mentioned.
        3. Identify 'EMOTIONAL_TONE' (e.g., symbolic, dark, redemptive, chaotic).
        4. List 'DISCARDED_NOISE' (parts of the text that are just conversational filler).
        
        Return ONLY valid JSON in this format:
        {
            "intent": "INTENT_NAME",
            "actors": ["actor1", "actor2"],
            "tone": "tone_description",
            "structured_summary": "Cleaned up version of the request",
            "discarded_noise": ["filler1", "filler2"]
        }
        """
        
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}

USER PROMPT: {raw_text}",
            "stream": False,
            "format": "json"
        }
        
        try:
            req = urllib.request.Request(
                self.ollama_url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return json.loads(result['response'])
        except Exception as e:
            print(f"BasketRouter: ❌ Error routing prompt: {e}")
            return {
                "intent": "FALLBACK",
                "structured_summary": raw_text,
                "error": str(e)
            }

if __name__ == "__main__":
    router = BasketRouter()
    # Test with a "messy" prompt style
    test_prompt = "so i was thinking, maybe the hand can move to d drive, and like, check the godot scripts, if they are bad purge them, if they are good cleanse them... judge them claude"
    print(json.dumps(router.route_prompt(test_prompt), indent=2))
