import os
import json
import time
import hashlib
from datetime import datetime

class VersionTracker:
    """
    Python implementation of VersionTracker for Devil's Hand.
    Tracks changes across the D: drive projects and links them to AI conversations.
    """
    def __init__(self, base_dir, history_dir):
        self.base_dir = base_dir
        self.history_dir = os.path.join(history_dir, "versions")
        self.index_path = os.path.join(self.history_dir, "version_index.json")
        
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
            
        self.version_index = self._load_index()
        self.file_snapshots = {} # path -> {mtime, hash}
        
        self.current_author = "Unknown"
        self.current_conversation_id = ""

    def _load_index(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_index(self):
        with open(self.index_path, 'w') as f:
            json.dump(self.version_index, f, indent=4)

    def set_author(self, author):
        self.current_author = author

    def set_conversation(self, conv_id):
        self.current_conversation_id = conv_id

    def track_file(self, file_path):
        """Creates a snapshot and records a version if changed."""
        if not os.path.exists(file_path):
            return None
            
        mtime = os.path.getmtime(file_path)
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        if file_path not in self.version_index:
            self.version_index[file_path] = {"versions": [], "current": 0}
            self._record_version(file_path, content, "Initial tracking")
        elif file_hash != self.version_index[file_path]["versions"][-1]["hash"]:
            self._record_version(file_path, content, "Auto-detected change")
            
        self.file_snapshots[file_path] = {"mtime": mtime, "hash": file_hash}
        return file_hash

    def _record_version(self, file_path, content, change_summary=""):
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        version_num = len(self.version_index.get(file_path, {}).get("versions", [])) + 1
        
        version_data = {
            "version": version_num,
            "timestamp": datetime.now().isoformat(),
            "author": self.current_author,
            "conversation_id": self.current_conversation_id,
            "summary": change_summary,
            "hash": file_hash,
            "size": len(content)
        }
        
        if file_path not in self.version_index:
            self.version_index[file_path] = {"versions": [], "current": 0}
            
        self.version_index[file_path]["versions"].append(version_data)
        self.version_index[file_path]["current"] = version_num
        
        # Save content to history
        safe_name = hashlib.sha1(file_path.encode('utf-8')).hexdigest()
        version_dir = os.path.join(self.history_dir, safe_name)
        if not os.path.exists(version_dir):
            os.makedirs(version_dir)
            
        version_file = os.path.join(version_dir, f"v{version_num:03d}.txt")
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self._save_index()
        print(f"VersionTracker: Saved v{version_num} for {file_path}")

    def get_history(self, file_path):
        return self.version_index.get(file_path, {}).get("versions", [])

    def rollback(self, file_path, version_num):
        safe_name = hashlib.sha1(file_path.encode('utf-8')).hexdigest()
        version_file = os.path.join(self.history_dir, safe_name, f"v{version_num:03d}.txt")
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._record_version(file_path, content, f"Rollback to v{version_num}")
            return True
        return False

if __name__ == "__main__":
    # Test
    vt = VersionTracker("D:/devil_s_hand", "D:/devil_s_hand/history")
    vt.set_author("Gemini")
    vt.track_file("D:/devil_s_hand/README.md")
