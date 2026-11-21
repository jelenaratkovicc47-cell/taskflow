# TaskFlow intent

## Problem

A small software team tracks work in messages and spreadsheets. Team members spend time piecing together who owns each task, what is blocked, and what is complete.

## Business goal

Give the team one shared board so everyone can see who owns the work, what needs attention, and what to pick up next.

## Users

- **Project manager** creates and assigns tasks, sets priorities, and tracks progress.
- **Developers** find assigned work and update its status as it moves through the board.
- **QA** finds work ready for review and checks when its status changed.

## Success criteria

- A valid task can be created, edited, retrieved, and displayed on the board. Missing required fields and duplicate task IDs produce clear errors. A duplicate ID creates no extra record.
- Each status change moves the task to the matching board column and records the time, previous status, and new status.
- The dashboard shows accurate totals, counts by status, and a count of high-priority tasks outside Done. The board’s assignee and priority filters match the stored tasks.
- A script creates at least 30 sample tasks across at least three assignees with varied statuses and priorities.
- Tasks and status history remain available after an application restart.
- Automated tests pass in GitHub Actions, and a new developer can start the app by following the README.
- The real Jira assessment issue links to the repository, CI run, final report, and progress history.

## Constraints

Use simulated project data only and free services. Use Python, FastAPI, SQLite, a simple HTML board, pytest, and GitHub Actions.

## In scope

Create, retrieve, and edit tasks. Each task has an ID, title, description, assignee, priority, status, and creation date. Track status changes across To Do, In Progress, In Review, and Done. Group tasks by status and show each task’s title, assignee, and priority. Provide assignee and priority filters, a dashboard with totals and recent activity, sample data, persistent storage, automated tests, and startup instructions.

## Out of scope

No real Jira integration, paid services, enterprise authentication, notifications, Gantt charts, or advanced permission system is required. Focus on the defined features and reliable behavior.

## Assumptions

TaskFlow covers one project, uses a fixed list of simulated assignees, and requires no login. Tasks can move from any status to any other status. The real Jira issue tracks the assessment separately from TaskFlow.

## Open questions

- Should users enter task IDs, or should TaskFlow generate them?
- Should the dashboard show recently created tasks, recent status changes, or both?
