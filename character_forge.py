import uuid

class CharacterForge:
    """
    Crafts, fine-tunes, and manages characters within the 5D story timelines.
    Each character has a look, story, job, and goals that drive the simulation.
    "Play game to program. Interact with it to change it."
    """
    def __init__(self, ecosystem):
        self.E = ecosystem
        self.characters = {} # id -> character data

    def craft_character(self, name, archetype, job, goal, appearance):
        char_id = str(uuid.uuid4())[:8]
        character = {
            "id": char_id,
            "name": name,
            "archetype": archetype,
            "job": job, # e.g., "Surgically removes glitches"
            "goal": goal, # e.g., "Make the perfect godot IDE"
            "appearance": appearance,
            "state": "idle", # idle, acting, simulating
            "current_timeline": "main" # For 5D tracking
        }
        self.characters[char_id] = character
        print(f"CharacterForge: 👤 Crafted character '{name}' the {archetype}.")
        
        self.E.push_event("character_crafted", character)
        return character

    def fine_tune(self, char_id, updates):
        """Fine-tune a character's traits based on story choices."""
        if char_id in self.characters:
            self.characters[char_id].update(updates)
            print(f"CharacterForge: 🔧 Fine-tuned character '{self.characters[char_id]['name']}'.")
            self.E.push_event("character_updated", self.characters[char_id])
            return self.characters[char_id]
        return None

    def get_all_characters(self):
        return list(self.characters.values())

if __name__ == "__main__":
    pass
