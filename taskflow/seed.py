from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import store


TITLES = (
    "Draft account setup checklist",
    "Confirm empty board behavior",
    "Write billing page help text",
    "Check mobile navigation",
    "Review search results layout",
    "Verify report export headers",
    "Document password reset steps",
    "Add sample customer records",
    "Review the onboarding form",
    "Check keyboard focus order",
    "Update release notes",
    "Verify date formatting",
    "Check the account settings page",
    "Review form validation messages",
    "Draft support handoff notes",
    "Check archived project visibility",
    "Update demo project labels",
    "Review the activity timeline",
    "Test the import preview",
    "Prepare test account data",
    "Review team invitation copy",
    "Check sorting on the reports page",
    "Verify profile field limits",
    "Draft the deployment checklist",
    "Review the help center links",
    "Check file upload feedback",
    "Update the support contact page",
    "Verify the settings confirmation",
    "Test report pagination",
    "Review the project overview",
)


def seed(path: Path) -> int:
    store.initialize(path)
    start = datetime(2026, 11, 12, 9, tzinfo=timezone.utc)
    with store.connect(path) as database:
        inserted = 0
        for index, title in enumerate(TITLES):
            inserted += store.create_task(database, {
                "task_id": f"TASK-{1001 + index}",
                "title": title,
                "description": f"Complete and document this simulated task: {title.lower()}.",
                "assignee": store.ASSIGNEES[index % len(store.ASSIGNEES)],
                "priority": store.PRIORITIES[(index // 3) % len(store.PRIORITIES)],
                "status": store.STATUSES[index % len(store.STATUSES)],
                "created_at": (start + timedelta(hours=index)).isoformat(timespec="microseconds"),
            })
    return inserted


if __name__ == "__main__":
    path = store.database_path()
    print(f"Added {seed(path)} sample tasks to {path}.")
