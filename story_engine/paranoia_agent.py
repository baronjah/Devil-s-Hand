import os
import time
import hashlib
import json
import re
from datetime import datetime

class ParanoiaAgent:
    """
    Self-aware codebase monitor. 
    Detects untracked changes, rapid edits, and breaking changes.
    """
    def __init__(self, watch_dirs):
        self.watch_dirs = watch_dirs
        self.signatures = {} # path -> {hash, mtime, func_sigs}
        self.alerts = []
        self.rapid_change_window = 10 # seconds
        self.recent_changes = [] # list of (path, timestamp)
        
        self._initialize_baseline()

    def _initialize_baseline(self):
        print("ParanoiaAgent: 👁️ Building baseline...")
        for d in self.watch_dirs:
            self._scan_dir(d)
        print(f"ParanoiaAgent: Baseline established for {len(self.signatures)} files.")

    def _scan_dir(self, dir_path):
        if not os.path.exists(dir_path):
            return
            
        for root, _, files in os.walk(dir_path):
            for f in files:
                if f.endswith(('.gd', '.py', '.js', '.html', '.md')):
                    path = os.path.join(root, f)
                    self._sign_file(path)

    def _sign_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            mtime = os.path.getmtime(path)
            
            # Extract GDScript function signatures
            func_sigs = {}
            if path.endswith('.gd'):
                matches = re.findall(r"func\s+(\w+)\s*\(([^)]*)\)", content)
                for name, params in matches:
                    func_sigs[name] = params
            
            self.signatures[path] = {
                "hash": file_hash,
                "mtime": mtime,
                "func_sigs": func_sigs
            }
        except:
            pass

    def check_integrity(self):
        """Runs a full check and returns alerts."""
        new_alerts = []
        current_time = time.time()
        
        # Cleanup old recent changes
        self.recent_changes = [c for c in self.recent_changes if current_time - c[1] < self.rapid_change_window]
        
        for path, old_sig in list(self.signatures.items()):
            if not os.path.exists(path):
                alert = {"type": "DELETED", "path": path, "severity": "critical", "msg": f"File deleted: {path}"}
                new_alerts.append(alert)
                del self.signatures[path]
                continue
                
            mtime = os.path.getmtime(path)
            if mtime != old_sig["mtime"]:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                new_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                
                if new_hash != old_sig["hash"]:
                    # File changed!
                    self.recent_changes.append((path, current_time))
                    
                    # Check for breaking changes in GDScript
                    if path.endswith('.gd'):
                        new_matches = re.findall(r"func\s+(\w+)\s*\(([^)]*)\)", content)
                        new_sigs = {name: params for name, params in new_matches}
                        
                        for func_name, old_params in old_sig["func_sigs"].items():
                            if func_name in new_sigs and new_sigs[func_name] != old_params:
                                alert = {
                                    "type": "BREAKING_CHANGE",
                                    "path": path,
                                    "severity": "critical",
                                    "msg": f"BREAKING: {os.path.basename(path)}.{func_name}() signature changed!"
                                }
                                new_alerts.append(alert)
                    
                    # Update signature
                    self._sign_file(path)
        
        # Check for rapid changes
        if len(self.recent_changes) >= 5:
            unique_files = len(set(c[0] for c in self.recent_changes))
            if unique_files >= 5:
                alert = {
                    "type": "MASS_CHANGE",
                    "severity": "critical",
                    "msg": f"ANOMALY: {unique_files} files changed in {self.rapid_change_window}s!"
                }
                new_alerts.append(alert)
                
        self.alerts.extend(new_alerts)
        return new_alerts

if __name__ == "__main__":
    pa = ParanoiaAgent(["D:/devil_s_hand", "D:/godot_projects/fab"])
    while True:
        alerts = pa.check_integrity()
        for a in alerts:
            print(f"[{a['severity'].upper()}] {a['msg']}")
        time.sleep(5)
