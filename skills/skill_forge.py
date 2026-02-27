import time
import uuid


def forge_skill_from_storyboard(storyboard: dict, requested_name: str = "") -> dict:
    story_id = storyboard.get("story_id", "unknown_story")
    beats = storyboard.get("beats", [])

    name = requested_name.strip() if requested_name.strip() else f"Skill from {storyboard.get('title', story_id)}"
    skill_id = "sk_" + uuid.uuid4().hex[:10]

    actions = []
    roles = set()
    for beat in beats:
        roles.update(beat.get("actors", []))
        actions.extend(beat.get("actions", []))

    manifest = {
        "skill_id": skill_id,
        "name": name,
        "version": "0.1.0",
        "schema_version": "1.0",
        "source_story_id": story_id,
        "story_roles": sorted(roles),
        "actions": sorted(set(actions)),
        "visual_profile": {
            "hand_theme": storyboard.get("theme_key", "default_infernal"),
            "cue_style": "demon_overlay",
            "pulse_palette": ["#ff3300", "#ff8800", "#220000"],
        },
        "dependencies": [],
        "compatibility": {
            "runtime": "devils_hand_v1",
            "surfaces": ["godot", "browser"],
        },
        "notes": {
            "beats_count": len(beats),
            "created_ms": int(time.time() * 1000),
            "devils_in_detail": True,
        },
        "updated_ms": int(time.time() * 1000),
    }
    return manifest
