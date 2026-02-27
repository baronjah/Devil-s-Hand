import json
from story_engine.paranoia_agent import ParanoiaAgent
from basket_router import BasketRouter

class SkillForge:
    """
    Forges the philosophical skills: 'Miracle It Away' and 'Demonic Prevention'.
    Reconstructs the AI interaction style of Cursor-like environments.
    """
    
    def __init__(self, ecosystem):
        self.E = ecosystem

    def miracle_it_away(self, target_id, raw_input):
        """
        Philosophical Skill: The Miracle.
        Takes messy/broken input and transforms it into a structured, 'perfect' state.
        In Cursor AI terms: 'Fix this'.
        """
        print(f"SkillForge: ✨ Executing 'Miracle It Away' on {target_id}...")
        
        # Use BasketRouter to clean the 'sin' (messy input)
        structured = self.E.router.route_prompt(f"MIRACLE_FIX: {raw_input}")
        
        # Apply the miracle to the story/script state
        # (This would be where the 'Redeem' logic from judgement_engine.gd is powered)
        miracle_event = {
            "skill": "miracle_it_away",
            "target": target_id,
            "transformation": structured,
            "timestamp": self.E.vt.track_file(target_id) if hasattr(self.E.vt, "track_file") else None
        }
        
        return miracle_event

    def demonic_prevention(self, target_path):
        """
        Philosophical Skill: Demonic Prevention.
        Uses the Paranoia Agent to strike down an anomaly before it manifests.
        In Cursor AI terms: 'Preventing the crash'.
        """
        print(f"SkillForge: 🛡️ Executing 'Demonic Prevention' on {target_path}...")
        
        # Check for anomalies
        alerts = self.E.pa.check_integrity()
        for alert in alerts:
            if alert["path"] == target_path and alert["severity"] == "critical":
                # The prevention: Rollback the 'sin' immediately
                print(f"SkillForge: ⚡ Prevention triggered! Striking down anomaly in {target_path}")
                self.E.vt.rollback(target_path, self.E.vt.get_history(target_path)[-2]["version"])
                return {"skill": "demonic_prevention", "status": "prevented", "alert": alert}
        
        return {"skill": "demonic_prevention", "status": "no_threat_detected"}

if __name__ == "__main__":
    # Internal forge test
    pass
