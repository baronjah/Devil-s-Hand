import copy
import time


def create_story_runtime(storyboard: dict) -> dict:
    return {
        "story_id": storyboard["story_id"],
        "state": "idle",
        "cursor": 0,
        "beats": copy.deepcopy(storyboard.get("beats", [])),
        "timeline": copy.deepcopy(storyboard.get("timeline", [])),
        "branches": {
            "main": {
                "cursor": 0,
                "beats": copy.deepcopy(storyboard.get("beats", [])),
            }
        },
        "canon_branch": "main",
        "snapshots": [],
        "current_snapshot": None,
        "last_merge": {},
    }


def tick_story_runtime(runtime: dict) -> None:
    if runtime.get("state") not in {"active", "shadow"}:
        return

    beats = runtime.get("beats", [])
    if not beats:
        runtime["state"] = "idle"
        return

    cursor = (int(runtime.get("cursor", 0)) + 1) % len(beats)
    runtime["cursor"] = cursor
    beat = beats[cursor]

    snap = {
        "story_id": runtime.get("story_id"),
        "cursor": cursor,
        "beat_id": beat.get("beat_id"),
        "scene": beat.get("scene"),
        "state": runtime.get("state"),
        "ts_ms": int(time.time() * 1000),
    }
    runtime["current_snapshot"] = snap
    runtime.setdefault("snapshots", []).append(snap)

    if len(runtime["snapshots"]) > 200:
        runtime["snapshots"] = runtime["snapshots"][-200:]


def rewind_story(runtime: dict, timeline_index: int) -> None:
    beats = runtime.get("beats", [])
    if not beats:
        runtime["cursor"] = 0
        return
    idx = max(0, min(int(timeline_index), len(beats) - 1))
    runtime["cursor"] = idx


def branch_story(runtime: dict, branch_name: str) -> None:
    src = runtime.get("branches", {}).get(runtime.get("canon_branch", "main"), {})
    runtime.setdefault("branches", {})[branch_name] = {
        "cursor": src.get("cursor", runtime.get("cursor", 0)),
        "beats": copy.deepcopy(src.get("beats", runtime.get("beats", []))),
    }


def merge_story(runtime: dict, branch_a: str, branch_b: str) -> dict:
    a = runtime.get("branches", {}).get(branch_a) or runtime.get("branches", {}).get("main", {})
    b = runtime.get("branches", {}).get(branch_b) or runtime.get("branches", {}).get("main", {})

    beats_a = a.get("beats", [])
    beats_b = b.get("beats", [])

    base = beats_a if len(beats_a) >= len(beats_b) else beats_b
    other = beats_b if base is beats_a else beats_a

    merged = []
    for i, beat in enumerate(base):
        row = copy.deepcopy(beat)
        if i < len(other):
            s1 = str(row.get("scene", ""))
            s2 = str(other[i].get("scene", ""))
            if s2 and s2 not in s1:
                row["scene"] = (s1 + " | " + s2).strip(" |")
        row["timeline_index"] = i
        merged.append(row)

    return {
        "branch_a": branch_a,
        "branch_b": branch_b,
        "merged_beats": merged,
        "merged_count": len(merged),
    }


def commit_canon(runtime: dict) -> dict:
    merged = runtime.get("last_merge", {}).get("merged_beats")
    if not merged:
        return {"committed": False, "reason": "no merge available"}

    runtime["beats"] = merged
    runtime["branches"]["main"] = {"cursor": 0, "beats": copy.deepcopy(merged)}
    runtime["canon_branch"] = "main"
    runtime["cursor"] = 0
    return {"committed": True, "beats": len(merged)}
