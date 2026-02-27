import time

class ModeManager:
    """
    Manages the 'Modes of Play Time' for Devil's Hand.
    Affects tick rates, possession rules, and story progression mechanics.
    """
    MODES = ["rpg", "action", "turn_based", "simulation", "sandbox", "survival"]

    def __init__(self, initial_mode="sandbox"):
        self.current_mode = initial_mode
        self.tick_rate = self._get_tick_rate(initial_mode)
        self.auto_advance_beats = self._get_auto_advance(initial_mode)

    def set_mode(self, new_mode):
        if new_mode in self.MODES:
            self.current_mode = new_mode
            self.tick_rate = self._get_tick_rate(new_mode)
            self.auto_advance_beats = self._get_auto_advance(new_mode)
            print(f"ModeManager: ⚙️ Switched to {new_mode.upper()} mode.")
            return True
        print(f"ModeManager: ❌ Invalid mode: {new_mode}")
        return False

    def _get_tick_rate(self, mode):
        """Returns the base tick interval in seconds for the Train Loop."""
        rates = {
            "action": 1.0,      # Fast, real-time feel
            "rpg": 3.0,         # Moderate pace
            "simulation": 2.0,  # Constant updates
            "sandbox": 5.0,     # Relaxed, player-driven
            "survival": 1.0,    # Fast, high stakes
            "turn_based": 0.5   # Very fast tick, but loop waits for turn flag
        }
        return rates.get(mode, 5.0)

    def _get_auto_advance(self, mode):
        """Whether the story automatically advances beats without explicit player input."""
        auto = {
            "action": True,      # Yes, story moves if you don't
            "rpg": False,        # Waits for dialogue/choices
            "simulation": True,  # World runs on its own
            "sandbox": False,    # Completely manual
            "survival": True,    # Time is always ticking
            "turn_based": False  # Strict turn blocks
        }
        return auto.get(mode, False)

    def process_loop_rules(self, ecosystem):
        """Applies mode-specific rules during the main train loop."""
        mode = self.current_mode
        
        if mode == "turn_based":
            # In turn-based, we only progress if a turn has been explicitly committed
            if not getattr(ecosystem, 'turn_committed', False):
                return False # Halt loop execution for this tick
            ecosystem.turn_committed = False # Reset for next turn
            
        elif mode == "survival":
            # Survival might drain resources every tick
            if hasattr(ecosystem, 'resources'):
                ecosystem.resources['energy'] = max(0, ecosystem.resources.get('energy', 100) - 1)
                
        # Sandbox might skip story beats entirely unless forced
        if mode == "sandbox" and not getattr(ecosystem, 'force_beat', False):
            return False

        return True # Proceed with normal loop

if __name__ == "__main__":
    mm = ModeManager()
    print(mm.current_mode, mm.tick_rate)
    mm.set_mode("action")
    print(mm.current_mode, mm.tick_rate)
