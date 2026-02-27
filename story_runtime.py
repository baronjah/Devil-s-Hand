import time
import json

class StoryRuntime:
    """
    Manages the 'Spirit of Time' logic for Devil's Hand.
    'Angel continues, Demon turns back and starts again.'
    """
    def __init__(self, ecosystem):
        self.E = ecosystem
        self.current_beat = 0
        self.history_stack = [] # Stack of successful beat IDs

    def angel_continue(self, beat_data):
        """The Angelic Path: Advance and Commit."""
        print("StoryRuntime: 👼 Angel continues the arc.")
        
        # 1. Commit the current state to VersionTracker
        self.E.vt.set_author("Angel")
        if "target_file" in beat_data:
            self.E.vt.track_file(beat_data["target_file"])
            
        # 2. Advance timeline
        self.current_beat += 1
        self.history_stack.append(self.current_beat)
        
        return {
            "spirit": "angel",
            "action": "CONTINUE",
            "beat_index": self.current_beat,
            "msg": "Timeline advanced and committed."
        }

    def demon_reset(self, target_file=None):
        """The Demonic Path: Turn back and start again."""
        print("StoryRuntime: 👹 Demon turns back and starts again.")
        
        # 1. Rollback the file to the previous version
        if target_file and os.path.exists(target_file):
            history = self.E.vt.get_history(target_file)
            if len(history) > 1:
                # Rollback to the version before the last one
                prev_v = history[-2]["version"]
                self.E.vt.rollback(target_file, prev_v)
        
        # 2. Reset the beat index to the last known 'good' point
        if self.history_stack:
            self.current_beat = self.history_stack.pop()
        else:
            self.current_beat = 0
            
        return {
            "spirit": "demon",
            "action": "RESET",
            "beat_index": self.current_beat,
            "msg": "Reality rejected. Timeline rolled back."
        }

import os
