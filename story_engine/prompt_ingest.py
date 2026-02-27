import time
import uuid


def ingest_prompt(raw_text: str, source: str = "user") -> dict:
    return {
        "prompt_id": "pr_" + uuid.uuid4().hex[:10],
        "source": source,
        "raw_text": raw_text.strip(),
        "created_ms": int(time.time() * 1000),
    }
