import os
import shutil
import json
from datetime import datetime

class BranchManager:
    """
    Manages physical 'Live Branches' on the drive.
    Allows forking the project into parallel versions within the D:/devil_s_hand/branches/ folder.
    """
    def __init__(self, base_dir="D:/devil_s_hand"):
        self.base_dir = base_dir
        self.branches_dir = os.path.join(base_dir, "branches")
        
        if not os.path.exists(self.branches_dir):
            os.makedirs(self.branches_dir)

    def fork_branch(self, branch_name):
        """Physically clones the current core files into a new branch folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = branch_name.lower().replace(" ", "_")
        target_dir = os.path.join(self.branches_dir, f"{safe_name}_{timestamp}")
        
        print(f"BranchManager: 🔱 Forking reality into {target_dir}...")
        
        # Files to copy (the core logic)
        extensions_to_copy = ['.py', '.gd', '.html', '.json', '.md', '.schema']
        # Folders to ignore (to avoid infinite recursion or huge data copies)
        ignore_folders = ['branches', 'archive', 'history', '.git', '__pycache__', 'logs']
        
        try:
            os.makedirs(target_dir)
            
            for item in os.listdir(self.base_dir):
                s = os.path.join(self.base_dir, item)
                d = os.path.join(target_dir, item)
                
                if os.path.isdir(s):
                    if item not in ignore_folders:
                        shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    if any(item.endswith(ext) for ext in extensions_to_copy):
                        shutil.copy2(s, d)
            
            print(f"BranchManager: ✅ Reality successfully forked.")
            return {
                "ok": True,
                "branch_path": target_dir,
                "name": branch_name,
                "timestamp": timestamp
            }
        except Exception as e:
            print(f"BranchManager: ❌ Fork failed: {e}")
            return {"ok": False, "error": str(e)}

    def list_branches(self):
        """Lists all physical branches on the drive."""
        if not os.path.exists(self.branches_dir): return []
        return os.listdir(self.branches_dir)

if __name__ == "__main__":
    pass
