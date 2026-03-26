#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path


INPUT_FILE = Path("anydo_storage_state.json")
OUTPUT_FULL = Path("anydo_export.json")
OUTPUT_COMPLETED = Path("anydo_completed_tasks.json")
OUTPUT_SUMMARY = Path("anydo_export_summary.json")

SENSITIVE_KEY_PARTS = (
    "token",
    "password",
    "auth",
    "idsalt",
)


def decode_value(node):
    if isinstance(node, list):
        return [decode_value(item) for item in node]

    if not isinstance(node, dict):
        return node

    if set(node.keys()) == {"valueEncoded"}:
        return decode_value(node["valueEncoded"])

    if set(node.keys()) == {"v"}:
        marker = node["v"]
        if marker in {"null", "undefined"}:
            return None
        return marker

    if set(node.keys()) == {"a", "id"}:
        return [decode_value(item) for item in node["a"]]

    if set(node.keys()) == {"o", "id"}:
        result = {}
        for pair in node["o"]:
            key = pair.get("k")
            result[key] = decode_value(pair.get("v"))
        return result

    return {key: decode_value(value) for key, value in node.items()}


def load_anydo_origin(storage_state):
    for origin in storage_state.get("origins", []):
        if origin.get("origin") == "https://app.any.do":
            return origin
    raise RuntimeError("Could not find https://app.any.do in storage state")


def load_anydo_sync_db(anydo_origin):
    for db in anydo_origin.get("indexedDB", []):
        if db.get("name") == "anydo-sync-db":
            return db
    raise RuntimeError("Could not find anydo-sync-db in IndexedDB export")


def redact_sensitive_fields(node):
    if isinstance(node, list):
        return [redact_sensitive_fields(item) for item in node]

    if isinstance(node, dict):
        redacted = {}
        for key, value in node.items():
            normalized_key = key.lower()
            if any(part in normalized_key for part in SENSITIVE_KEY_PARTS):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_sensitive_fields(value)
        return redacted

    return node


def main():
    if not INPUT_FILE.exists():
        raise RuntimeError(f"Missing input file: {INPUT_FILE}")

    storage_state = json.loads(INPUT_FILE.read_text())
    anydo_origin = load_anydo_origin(storage_state)
    sync_db = load_anydo_sync_db(anydo_origin)

    stores = {}
    store_counts = {}

    for store in sync_db.get("stores", []):
        store_name = store.get("name")
        decoded_records = [decode_value(record) for record in store.get("records", [])]
        stores[store_name] = decoded_records
        store_counts[store_name] = len(decoded_records)

    tasks = stores.get("task", [])
    completed_tasks = [task for task in tasks if task.get("status") == "CHECKED"]
    active_tasks = [task for task in tasks if task.get("status") != "CHECKED"]

    export_payload = {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "source": "Any.do web IndexedDB (anydo-sync-db)",
        "origin": anydo_origin.get("origin"),
        "database": sync_db.get("name"),
        "databaseVersion": sync_db.get("version"),
        "storeCounts": store_counts,
        "taskCounts": {
            "all": len(tasks),
            "completed": len(completed_tasks),
            "active": len(active_tasks),
        },
        "stores": stores,
    }

    export_payload = redact_sensitive_fields(export_payload)

    completed_payload = {
        "exportedAt": export_payload["exportedAt"],
        "source": export_payload["source"],
        "taskCounts": export_payload["taskCounts"],
        "completedTasks": completed_tasks,
    }

    summary_payload = {
        "exportedAt": export_payload["exportedAt"],
        "database": export_payload["database"],
        "storeCounts": store_counts,
        "taskCounts": export_payload["taskCounts"],
        "outputFiles": [
            str(OUTPUT_FULL),
            str(OUTPUT_COMPLETED),
            str(OUTPUT_SUMMARY),
        ],
    }

    OUTPUT_FULL.write_text(json.dumps(export_payload, indent=2, ensure_ascii=False))
    OUTPUT_COMPLETED.write_text(json.dumps(completed_payload, indent=2, ensure_ascii=False))
    OUTPUT_SUMMARY.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False))

    print(json.dumps(summary_payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
