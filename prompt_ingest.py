import os
import json
import uuid
from datetime import datetime

class PromptIngest:
    """
    Handles the physical ingestion of prompts into the Devil's Hand ecosystem.
    Saves raw logs and hands off to the BasketRouter.
    """
    def __init__(self, base_dir="D:/devil_s_hand"):
        self.logs_dir = os.path.join(base_dir, "logs", "prompts")
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def ingest(self, raw_text, source="user_terminal"):
        prompt_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "prompt_id": prompt_id,
            "timestamp": timestamp,
            "source": source,
            "raw_text": raw_text
        }
        
        # Save raw log
        log_path = os.path.join(self.logs_dir, f"{prompt_id}.json")
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=4)
            
        return log_entry

if __name__ == "__main__":
    ingestor = PromptIngest()
    print(ingestor.ingest("Test prompt for ingestion"))
