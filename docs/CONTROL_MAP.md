# Control Map

This file defines who controls what now in Devil's Hand (`devil_s_hand` / `j_s_hand`).

## Control Authorities

- `user` (`JSH`): final director authority, approves critical control actions, can force override.
- `ai`: co-author and co-controller during token turns.
- `devil_s_hand`: ecosystem conductor (scheduler, queue, state, safety gate).
- `j_s_hand`: human-identity alias used for signature and ownership paths.

## Runtime Ownership

- Story intent parsing: `devil_s_hand` + `ancient_screenwriters` cast.
- Storyboard canon decisions: `user` final, AI proposes and scores.
- Possession turns: token scheduler in `control/possession_engine.py`.
- Real-world execution: blocked by default until simulation gate passes.

## Control States

- `simulation_only`: all proposed actions execute as simulation.
- `approved_real_control`: unlocked only after explicit gate pass.
- `emergency_override`: user can seize immediate control.

## Branch Ownership

- `gemini-cli`: Gemini branch with independent workstream.
- `codex/Luminus`: Codex branch for Devil's Hand control/pathway system.
