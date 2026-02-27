import re

STOP_WORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "it", "is", "are", "be",
    "this", "that", "for", "on", "with", "as", "at", "we", "i", "you"
}

ACTION_HINTS = [
    "build", "make", "create", "move", "switch", "run", "start", "stop", "rewind",
    "merge", "save", "load", "possess", "control", "theme", "story", "skill"
]


def _split_chunks(text: str):
    return [c.strip() for c in re.split(r"[,;\n]+", text) if c.strip()]


def _is_noise(chunk: str) -> bool:
    tokens = re.findall(r"[a-zA-Z0-9_']+", chunk.lower())
    if not tokens:
        return True
    meaningful = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
    return len(meaningful) == 0


def _intent(chunk: str) -> dict:
    lower = chunk.lower()
    tags = [a for a in ACTION_HINTS if a in lower]

    if "story" in lower or "scene" in lower:
        domain = "story"
    elif "skill" in lower:
        domain = "skill"
    elif "theme" in lower or "shader" in lower or "visual" in lower:
        domain = "visual"
    elif "control" in lower or "possess" in lower:
        domain = "possession"
    else:
        domain = "general"

    confidence = min(0.98, 0.35 + 0.1 * len(tags))
    return {
        "text": chunk,
        "domain": domain,
        "tags": sorted(set(tags)),
        "confidence": round(confidence, 3),
    }


def _story_targets(text: str):
    out = set()
    for m in re.finditer(r"story\s*[:=]\s*([a-zA-Z0-9_\-]+)", text, flags=re.IGNORECASE):
        out.add(m.group(1))
    for m in re.finditer(r"#([a-zA-Z0-9_\-]+)", text):
        out.add(m.group(1))
    return sorted(out)


def route_prompt(prompt_row: dict) -> dict:
    raw = prompt_row.get("raw_text", "")
    intents = []
    discarded = []

    for chunk in _split_chunks(raw):
        if _is_noise(chunk):
            discarded.append(chunk)
            continue
        intents.append(_intent(chunk))

    if intents:
        confidence = round(sum(i["confidence"] for i in intents) / len(intents), 3)
    else:
        confidence = 0.15

    return {
        "prompt_id": prompt_row.get("prompt_id", ""),
        "raw_text": raw,
        "intents": intents,
        "story_targets": _story_targets(raw),
        "discarded_noise": discarded,
        "confidence": confidence,
    }
