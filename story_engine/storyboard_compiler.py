import time
import uuid


def compile_storyboard(basket: dict, title: str = "") -> dict:
    story_id = "st_" + uuid.uuid4().hex[:10]
    intents = basket.get("intents", [])

    beats = []
    for i, intent in enumerate(intents):
        beats.append({
            "beat_id": f"bt_{i:03d}",
            "story_id": story_id,
            "scene": intent.get("text", "Untitled scene"),
            "actors": ["user", "ai", "devils_hand"],
            "actions": intent.get("tags", ["observe"]),
            "timeline_index": i,
            "visual_cue": intent.get("domain", "general"),
            "detail_weight": round(0.4 + (0.1 * len(intent.get("tags", []))), 3),
        })

    if not beats:
        beats = [{
            "beat_id": "bt_000",
            "story_id": story_id,
            "scene": basket.get("raw_text", "Empty prompt"),
            "actors": ["user", "ai"],
            "actions": ["observe"],
            "timeline_index": 0,
            "visual_cue": "general",
            "detail_weight": 0.4,
        }]

    timeline = [{
        "timeline_index": b["timeline_index"],
        "beat_id": b["beat_id"],
        "event": "beat_ready",
        "ts_ms": int(time.time() * 1000),
    } for b in beats]

    final_title = title.strip() if title and title.strip() else beats[0]["scene"][:60]
    if not final_title:
        final_title = "Devils Hand Story"

    return {
        "story_id": story_id,
        "title": final_title,
        "theme_key": "default_infernal",
        "source_prompt_id": basket.get("prompt_id", ""),
        "beats": beats,
        "actors": [
            {"id": "user", "role": "director"},
            {"id": "ai", "role": "co_author"},
            {"id": "devils_hand", "role": "operator"},
        ],
        "tasks": [{
            "task_id": f"tsk_{i:03d}",
            "beat_id": b["beat_id"],
            "action": ",".join(b.get("actions", [])),
            "requires_approval": True,
            "phase": "simulation",
        } for i, b in enumerate(beats)],
        "timeline": timeline,
        "updated_ms": int(time.time() * 1000),
    }
