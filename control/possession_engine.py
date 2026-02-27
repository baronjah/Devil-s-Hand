import time


class PossessionEngine:
    def __init__(self, base_turn_ms: int = 10000, bonus_multiplier: float = 1.5, max_bonus_factor: float = 2.0):
        self.base_turn_ms = int(base_turn_ms)
        self.bonus_multiplier = float(bonus_multiplier)
        self.max_bonus_factor = float(max_bonus_factor)

        self.character_id = "main_character"
        self.controller = "shared"
        self.turn_owner = "user"
        self.turn_started_at = int(time.time() * 1000)
        self.turn_duration_ms = self.base_turn_ms
        self.bonus_applied = False
        self.override_available = True

        self.user_control_ms = 0
        self.ai_control_ms = 0
        self._last_tick = self.turn_started_at

    def _now(self) -> int:
        return int(time.time() * 1000)

    def _apply_elapsed(self, now_ms: int) -> None:
        elapsed = max(0, now_ms - self._last_tick)
        if self.turn_owner == "user":
            self.user_control_ms += elapsed
        elif self.turn_owner == "ai":
            self.ai_control_ms += elapsed
        self._last_tick = now_ms

    def _calc_user_bonus_turn(self) -> int:
        total = self.user_control_ms + self.ai_control_ms
        if total <= 0:
            return self.base_turn_ms
        user_share = self.user_control_ms / float(total)
        if user_share >= 0.45:
            return self.base_turn_ms

        boosted = int(self.base_turn_ms * self.bonus_multiplier)
        cap = int(self.base_turn_ms * self.max_bonus_factor)
        return min(boosted, cap)

    def tick(self) -> None:
        now_ms = self._now()
        self._apply_elapsed(now_ms)

        if now_ms - self.turn_started_at >= self.turn_duration_ms:
            if self.turn_owner == "user":
                self.turn_owner = "ai"
                self.turn_duration_ms = self.base_turn_ms
                self.bonus_applied = False
            else:
                self.turn_owner = "user"
                boosted = self._calc_user_bonus_turn()
                self.turn_duration_ms = boosted
                self.bonus_applied = boosted > self.base_turn_ms
            self.turn_started_at = now_ms

    def request_control(self, side: str, character_id: str = "main_character", emergency_override: bool = False) -> dict:
        side = "user" if side not in {"user", "ai"} else side
        now_ms = self._now()
        self._apply_elapsed(now_ms)

        if emergency_override and side == "user":
            self.turn_owner = "user"
            self.turn_started_at = now_ms
            self.turn_duration_ms = self._calc_user_bonus_turn()
            self.bonus_applied = self.turn_duration_ms > self.base_turn_ms
            self.controller = "shared"
            self.character_id = character_id
            return {"ok": True, "mode": "emergency_override", **self.get_state()}

        self.character_id = character_id
        self.controller = "shared"
        self.turn_owner = side
        self.turn_started_at = now_ms
        self.turn_duration_ms = self.base_turn_ms
        self.bonus_applied = False
        return {"ok": True, "mode": "request", **self.get_state()}

    def release_control(self, side: str) -> dict:
        now_ms = self._now()
        self._apply_elapsed(now_ms)

        if side == self.turn_owner:
            self.turn_owner = "ai" if side == "user" else "user"
            self.turn_started_at = now_ms
            self.turn_duration_ms = self.base_turn_ms
            self.bonus_applied = False
        return {"ok": True, "mode": "release", **self.get_state()}

    def get_state(self) -> dict:
        return {
            "character_id": self.character_id,
            "controller": self.controller,
            "turn_owner": self.turn_owner,
            "turn_started_at": self.turn_started_at,
            "turn_duration_ms": self.turn_duration_ms,
            "bonus_applied": self.bonus_applied,
            "override_available": self.override_available,
            "user_control_ms": self.user_control_ms,
            "ai_control_ms": self.ai_control_ms,
        }
