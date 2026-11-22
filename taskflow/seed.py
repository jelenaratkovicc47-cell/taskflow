from datetime import datetime, timedelta, timezone
from itertools import chain
from pathlib import Path

from . import store


ORIGINAL_TITLES = (
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

ADDITIONAL_TASKS = (
    ("Map the account recovery flow", "Document the steps from a forgotten password to a successful sign-in."),
    ("Check document upload limits", "Verify the file size limit and the message shown when an upload exceeds it."),
    ("Draft the weekly release brief", "Summarize what shipped and list the items still awaiting review."),
    ("Review the billing history screen", "Check that invoice dates, amounts, and download links are easy to find."),
    ("Test invitation expiry", "Confirm that an expired invitation shows a clear recovery action."),
    ("Update the customer handoff checklist", "Add an owner and a verification step to every handoff item."),
    ("Audit project summary labels", "Compare the dashboard labels with the terms used in the project board."),
    ("Verify the import error report", "Import a sample file with invalid rows and check that it identifies each row."),
    ("Prepare reviewer demo accounts", "Create fictional demo accounts for the product walkthrough."),
    ("Design the empty search state", "Describe what viewers should see before a search and when it returns no results."),
    ("Check large report downloads", "Export the largest sample report and verify its row count and file name."),
    ("Refresh the support FAQ", "Update answers for the most common account and project setup questions."),
    ("Review priority labels for accessibility", "Check that users can distinguish all priorities from their text labels."),
    ("Test combined report filters", "Compare filters used alone and together against a hand-checked sample."),
    ("Outline the upcoming release demo", "Prepare a walkthrough covering setup, normal usage, and a recoverable error."),
    ("Clarify workspace setup instructions", "Review the steps shown when a project manager opens a workspace for the first time."),
    ("Verify keyboard access to filters", "Use the keyboard to open, apply, and clear the filters in a browser."),
    ("Document known demo limitations", "Describe the simulated data and the scope of the local environment."),
    ("Review mobile account settings", "Check that the settings actions remain visible on a narrow screen."),
    ("Test cancellation of an edit", "Open the edit form, change a field, cancel, and confirm the stored value stays the same."),
    ("Prepare the project review agenda", "List the features to demonstrate and the questions for the review team."),
    ("Draft accessible form hints", "Write short hints for task IDs, required fields, and valid input formats."),
    ("Check recovery after a failed save", "Use a sample form to verify that unsubmitted values can be corrected and resubmitted."),
    ("Write the first-run troubleshooting guide", "Cover setup errors such as a missing dependency or a port already in use."),
    ("Review task detail formatting", "Check long descriptions and task titles in the detail view at different widths."),
    ("Verify the latest-task ordering", "Create tasks at known times and confirm the newest appears first in the summary."),
    ("Prepare the QA sign-off checklist", "Document the scenarios reviewers should run before accepting the release."),
    ("Review the project review screen", "Check that owners, priorities, and statuses are understandable without color cues."),
    ("Compare workload totals to stored tasks", "Count open tasks per assignee independently and compare the dashboard figures."),
    ("Capture the release demo notes", "Record the final test result and the steps used to reproduce the demo."),
)


def seed(path: Path) -> int:
    store.initialize(path)
    start = datetime(2026, 11, 12, 9, tzinfo=timezone.utc)
    original = (
        (title, f"Complete and document this simulated task: {title.lower()}.", store.ASSIGNEES[index % 3])
        for index, title in enumerate(ORIGINAL_TITLES)
    )
    additional = (
        (title, description, store.ASSIGNEES[3 + index % 3])
        for index, (title, description) in enumerate(ADDITIONAL_TASKS)
    )
    with store.connect(path) as database:
        inserted = 0
        for index, (title, description, assignee) in enumerate(chain(original, additional)):
            inserted += store.create_task(database, {
                "task_id": f"TASK-{1001 + index}",
                "title": title,
                "description": description,
                "assignee": assignee,
                "priority": store.PRIORITIES[(index // 3) % len(store.PRIORITIES)],
                "status": store.STATUSES[index % len(store.STATUSES)],
                "created_at": (start + timedelta(hours=index)).isoformat(timespec="microseconds"),
            })
    return inserted


if __name__ == "__main__":
    path = store.database_path()
    print(f"Added {seed(path)} sample tasks to {path}.")
