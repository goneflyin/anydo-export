#!/usr/bin/env python3
import json
from pathlib import Path


INPUT_FILE = Path("anydo_export.json")
OUTPUT_FILE = Path("anydo_export_flat.json")


def load_json(path: Path):
    if not path.exists():
        raise RuntimeError(f"Missing file: {path}")
    return json.loads(path.read_text())


def build_flat_export(data):
    stores = data.get("stores", {})
    categories = stores.get("category", [])
    tags = stores.get("tag", [])
    labels = stores.get("label", [])
    tasks = stores.get("task", [])

    list_by_id = {category.get("id"): category for category in categories if category.get("id")}
    tag_by_id = {tag.get("id"): tag for tag in tags if tag.get("id")}
    label_by_id = {label.get("id"): label for label in labels if label.get("id")}

    flat_tasks = []
    for task in tasks:
        list_info = list_by_id.get(task.get("categoryId"), {})

        task_labels = []
        for label_id in task.get("labels", []) or []:
            label_info = label_by_id.get(label_id)
            if label_info:
                task_labels.append(
                    {
                        "id": label_info.get("id"),
                        "name": label_info.get("name"),
                        "color": label_info.get("color"),
                    }
                )
            else:
                task_labels.append({"id": label_id, "name": None, "color": None})

        flat_tasks.append(
            {
                "taskId": task.get("id"),
                "globalTaskId": task.get("globalTaskId"),
                "title": task.get("title"),
                "note": task.get("note"),
                "status": task.get("status"),
                "isCompleted": task.get("status") == "CHECKED",
                "priority": task.get("priority"),
                "dueDate": task.get("dueDate"),
                "alert": task.get("alert"),
                "repeatMethod": task.get("repeatingMethod"),
                "listId": task.get("categoryId"),
                "listName": list_info.get("name"),
                "isGroceryList": list_info.get("isGroceryList"),
                "parentTaskId": task.get("parentGlobalTaskId"),
                "subTasks": task.get("subTasks") or [],
                "labels": task_labels,
                "tags": [
                    {
                        "id": tag_id,
                        "name": tag_by_id.get(tag_id, {}).get("name"),
                    }
                    for tag_id in (task.get("tags") or [])
                ],
                "participants": task.get("participants") or [],
                "location": {
                    "latitude": task.get("latitude"),
                    "longitude": task.get("longitude"),
                },
                "timestamps": {
                    "createdMs": task.get("creationDate"),
                    "updatedMs": task.get("lastUpdateDate"),
                    "statusUpdatedMs": task.get("statusUpdateTime"),
                    "dueDateUpdatedMs": task.get("dueDateUpdateTime"),
                },
            }
        )

    return {
        "exportedAt": data.get("exportedAt"),
        "source": data.get("source"),
        "taskCounts": {
            "all": len(flat_tasks),
            "completed": sum(1 for task in flat_tasks if task["isCompleted"]),
            "active": sum(1 for task in flat_tasks if not task["isCompleted"]),
        },
        "lists": [
            {
                "listId": category.get("id"),
                "name": category.get("name"),
                "isDefault": category.get("isDefault"),
                "isGroceryList": category.get("isGroceryList"),
                "isDeleted": category.get("isDeleted"),
            }
            for category in categories
        ],
        "tags": [
            {
                "tagId": tag.get("id"),
                "name": tag.get("name"),
            }
            for tag in tags
        ],
        "labels": [
            {
                "labelId": label.get("id"),
                "name": label.get("name"),
                "color": label.get("color"),
            }
            for label in labels
        ],
        "tasks": flat_tasks,
    }


def main():
    data = load_json(INPUT_FILE)
    flat = build_flat_export(data)
    OUTPUT_FILE.write_text(json.dumps(flat, indent=2, ensure_ascii=False))
    print(
        json.dumps(
            {
                "output": str(OUTPUT_FILE),
                "tasks": flat["taskCounts"],
                "lists": len(flat["lists"]),
                "tags": len(flat["tags"]),
                "labels": len(flat["labels"]),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
