import os
import json
import shutil
import time
from datetime import datetime
from schemas.swiss_knife_schema import SwissKnifeSchema

class SaveSystem:
    """
    Manages the JSON-first archive/chunk/cache lifecycle for Devil's Hand.
    Handles saving, loading, and archiving ecosystem states.
    Uses SwissKnifeSchema for structured payloads.
    """
    def __init__(self, base_dir="D:/devil_s_hand"):
        self.snapshots_dir = os.path.join(base_dir, "snapshots")
        self.archive_dir = os.path.join(base_dir, "archive")
        
        for d in [self.snapshots_dir, self.archive_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

    def create_empty_state(self, user_id="JSH"):
        return SwissKnifeSchema.create_save_payload(user_id)

    def save_state(self, state_dict, save_name="auto_save", tag="runtime"):
        """Saves a JSON snapshot of the ecosystem."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{save_name}_{tag}_{timestamp}.json"
        filepath = os.path.join(self.snapshots_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, indent=4)
            print(f"SaveSystem: 💾 Saved state to {filename}")
            
            # Simple chunking/archiving: Keep only last 10 snapshots of this name
            self._enforce_retention(save_name, max_keeps=10)
            return filepath
        except Exception as e:
            print(f"SaveSystem: ❌ Error saving state: {e}")
            return None

    def load_latest(self, save_name="auto_save"):
        """Loads the most recent snapshot for a given save name."""
        files = [f for f in os.listdir(self.snapshots_dir) if f.startswith(save_name)]
        if not files:
            return None
            
        # Sort by timestamp (descending)
        files.sort(reverse=True)
        latest_file = os.path.join(self.snapshots_dir, files[0])
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            print(f"SaveSystem: 📂 Loaded state from {files[0]}")
            return state
        except Exception as e:
            print(f"SaveSystem: ❌ Error loading state: {e}")
            return None

    def _enforce_retention(self, save_name, max_keeps=10):
        """Moves old snapshots to archive to save active space."""
        files = [f for f in os.listdir(self.snapshots_dir) if f.startswith(save_name)]
        files.sort(reverse=True) # Newest first
        
        if len(files) > max_keeps:
            to_archive = files[max_keeps:]
            for f in to_archive:
                src = os.path.join(self.snapshots_dir, f)
                dst = os.path.join(self.archive_dir, f)
                shutil.move(src, dst)
            print(f"SaveSystem: 📦 Archived {len(to_archive)} old snapshots.")

if __name__ == "__main__":
    s = SaveSystem()
    s.save_state({"test": "data", "mode": "sandbox"}, "test_save")
