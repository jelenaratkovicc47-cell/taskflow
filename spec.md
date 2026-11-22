# TaskFlow specification

## Application and data

TaskFlow serves one simulated project. A FastAPI app renders a plain HTML board, dashboard, and task forms. Route handlers share validation and task operations. SQLite stores data in a local file whose path can be set for tests and demos. The default startup uses localhost. The project manager, developers, and QA use the same screens without logging in.

| Record | Fields and rules |
| --- | --- |
| Task | `task_id` is a unique, immutable text ID entered at creation. Trim whitespace and normalize to uppercase. Accept `TASK-` followed by a positive integer without leading zeros. Title and description must contain text after trimming. Assignee and priority must be from the lists below. The server sets the initial status to To Do and records the creation time in UTC. |
| Status change | A unique entry ID, the task ID, previous status, new status, and change time in UTC. The task ID references an existing task. Record each change in the same transaction that updates the task. |

- Assignees are Maya, Leo, Nina, Avery, Omar, and Priya. Priorities are Low, Medium, and High.
- Every status can move to any other status. Submitting the current status succeeds with zero new history entries. Creating or editing a task produces zero status changes.
- The sample-data script inserts 60 tasks with deterministic IDs, all four statuses, all three priorities, and six assignees. Existing sample IDs retain their original data, and rerunning the script adds any missing sample tasks while preserving edits. Seeded tasks represent a starting snapshot.

## Screens and routes

| Action | Route | Expected behavior |
| --- | --- | --- |
| View board | `GET /` | Show To Do, In Progress, In Review, and Done in that order, including empty columns. Each card shows its title, assignee, and priority and links to the task. Optional `assignee` and `priority` filters can be used independently or together. When combined, a card must satisfy both. |
| Create a task | `GET /tasks/new`, `POST /tasks` | Show the task ID, title, description, assignee, and priority fields. On success, redirect to the task detail. |
| View a task | `GET /tasks/{task_id}` | Show every task field and status history, most recent first. |
| Edit task details | `GET /tasks/{task_id}/edit`, `POST /tasks/{task_id}/edit` | Allow changes to title, description, assignee, and priority. Redirect to the task detail on success. |
| Change status | `POST /tasks/{task_id}/status` | Submit a status from the task detail page and redirect back on success. The detail and board reflect the saved status. |
| View dashboard | `GET /dashboard` | Show project-wide totals, active work (In Progress and In Review), workflow counts, completion percentage, and high-priority tasks outside Done. Display each assignee's open-task count with a link to their board view. Show the five newest tasks with their assignee, priority, status, and creation date. Board filters apply only to the board. |

Show field-specific explanations and preserve entered values when a form is invalid. Return HTTP 422 for missing or invalid input, 409 for a duplicate task ID, and 404 for a task that does not exist. Invalid submissions preserve stored tasks and history. Use HTTP 303 after successful form submissions so refreshing the destination does not resubmit the form.

## Acceptance checks

| Requirement | Verification |
| --- | --- |
| Create, edit, and retrieve | Submit a valid task, view it on the board and detail page, edit all four editable fields, and verify the saved values. |
| Clear validation and duplicate handling | Submit missing or blank fields, unsupported values, and a duplicate ID. Verify the response identifies the problem and the task count stays unchanged. |
| Status and history | Move a task between two columns, then move it back. Verify its placement and the previous status, new status, and time of both entries. Repeating the current status leaves the history count unchanged. |
| Counts, filters, and recent tasks | Use a known set of tasks to check exact dashboard counts, completion percentage, and per-assignee open workload. Exclude Done tasks from the open counts and verify single and combined board filters. Check recent task ordering and the five-task limit. Confirm that an empty project shows zero totals. |
| Sample data and persistence | Run the seed script on a fresh database and confirm 60 tasks across six assignees with the required variety. Repeat the seed without increasing the count. Reopen the same file through a fresh app instance and verify a saved task and its history. |
| Reproducible run and CI | Follow the README from a clean environment. Verify the board in a browser and confirm pytest passes in GitHub Actions. |
| Assessment evidence | Verify the real Jira issue has dated progress updates and links to the repository, CI run, and final report. |
