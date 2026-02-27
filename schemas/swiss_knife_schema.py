import time
import uuid

class SwissKnifeSchema:
    """
    Python implementation of the Swiss Knife System Schema for Devil's Hand.
    Provides structured entity factories for the JSON-first data model.
    """
    
    # Entity Types
    ITEM_TYPES = ["PART", "TOOL", "NODE", "ACTOR", "MAP_OBJECT"]
    STAGES = ["DRAFT", "QUEUED", "PROCESSING", "DONE", "ARCHIVED"]
    BRANCH_TYPES = ["LOGIC_BLOCK", "SCENARIO", "PROCESS", "GROUP"]
    LINE_ROLES = ["FLOW", "DEPENDENCY", "VALIDATION", "TRIGGER"]
    GATE_TYPES = ["STATE_CHECK", "RESOURCE_CHECK", "TIMER_CHECK", "USER_PERMISSION"]

    @staticmethod
    def create_item(item_type, label="new_item"):
        return {
            "item_id": str(uuid.uuid4()),
            "label": label,
            "type": item_type,
            "stage": "DRAFT",
            "state": {},
            "position": {"x": 0, "y": 0, "z": 0},
            "metadata": {}
        }

    @staticmethod
    def create_branch_node(label, branch_type="LOGIC_BLOCK"):
        return {
            "branch_id": str(uuid.uuid4()),
            "label": label,
            "branch_type": branch_type,
            "state": {},
            "parent_id": None,
            "children": [],
            "position": {"x": 0, "y": 0}
        }

    @staticmethod
    def create_line(from_id, to_id, role="FLOW"):
        return {
            "line_id": str(uuid.uuid4()),
            "from_id": from_id,
            "to_id": to_id,
            "role": role,
            "state": {},
            "gates": []
        }

    @staticmethod
    def create_timeline_event(user_id, action, target_id):
        return {
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "timestamp": time.time(),
            "action": action,
            "target_id": target_id,
            "before": {},
            "after": {}
        }

    @staticmethod
    def create_save_payload(user_id="JSH"):
        return {
            "meta": {
                "schema_version": 3,
                "user": user_id,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            },
            "windows": {},
            "scene": {},
            "branches": {},
            "lines": {},
            "gates": {},
            "timeline": [],
            "custom": {}
        }

if __name__ == "__main__":
    # Test
    payload = SwissKnifeSchema.create_save_payload()
    node = SwissKnifeSchema.create_branch_node("Root Process")
    payload["branches"][node["branch_id"]] = node
    print(json.dumps(payload, indent=2))
