import os
import json
import uuid
from schemas.swiss_knife_schema import SwissKnifeSchema

class DimensionExplorer:
    """
    Handles roaming, expectations, checking, and creation across the drive.
    "We go there, we check, we use if we can... we might need to create it."
    """
    def __init__(self, ecosystem):
        self.E = ecosystem
        self.current_path = "D:/"
        self.expectations = [] # List of {id, text, status: pending|met|failed}
        self.reality = {} # path -> stats

    def roam(self, target_path):
        """Moves the Hand to a new dimension."""
        target_path = target_path.replace("", "/")
        if os.path.exists(target_path):
            self.current_path = target_path
            print(f"DimensionExplorer: 🖐️ Roamed to {target_path}")
            return True
        print(f"DimensionExplorer: ❌ Target dimension does not exist: {target_path}")
        return False

    def declare_expectation(self, expectation_text):
        """Uses LLM to define what 'should' be in this dimension."""
        print(f"DimensionExplorer: 📜 Expecting: '{expectation_text}' at {self.current_path}")
        
        # In a full flow, we'd use the LLM to parse this into a manifest.
        # For now, we create a symbolic expectation entry.
        expectation = {
            "id": str(uuid.uuid4())[:8],
            "text": expectation_text,
            "path": self.current_path,
            "status": "pending"
        }
        self.expectations.append(expectation)
        return expectation

    def check_reality(self):
        """Scans current path and compares against expectations."""
        if not os.path.exists(self.current_path):
            return {"error": "Dimension missing"}
            
        files = os.listdir(self.current_path)
        self.reality = {
            "path": self.current_path,
            "file_count": len(files),
            "files": files[:20], # Truncated list
            "is_empty": len(files) == 0
        }
        
        # Simple verification logic
        for exp in self.expectations:
            if exp["path"] == self.current_path:
                # If expectation text matches a filename (primitive check)
                found = any(exp["text"].lower() in f.lower() for f in files)
                exp["status"] = "met" if found else "failed"
                
        return self.reality

    def reconstruct(self, expectation_id):
        """Forgets the 'failed' reality and miracles the expected data into existence."""
        exp = next((e for e in self.expectations if e["id"] == expectation_id), None)
        if not exp: return False
        
        print(f"DimensionExplorer: 🔨 Reconstructing dimension to meet expectation: {exp['text']}")
        
        # The 'Miracle': Create a file that matches the expectation
        safe_filename = exp["text"].lower().replace(" ", "_")[:20] + ".gd"
        target_file = os.path.join(exp["path"], safe_filename)
        
        if not os.path.exists(target_file):
            content = f"## Reconstructed by Devil's Hand
## Expectation: {exp['text']}
extends Node

func _ready():
	print('Reality forged.')
"
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            exp["status"] = "met"
            self.E.vt.track_file(target_file) # Track the new creation
            return True
        return False

if __name__ == "__main__":
    pass
