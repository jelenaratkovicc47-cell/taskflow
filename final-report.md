# TaskFlow assessment report

## Problem and delivery

A small software team needed one place to see task ownership, priority, and progress. TaskFlow provides a board for the project manager, developers, and QA. It runs locally with one simulated project and three assignees.

- [Intent](intent.md) defines the business goal, scope, and success criteria.
- [Specification](spec.md) defines behavior, the data model, and verification checks.
- [Delivery plan](plan.md) maps implementation, testing, CI, and submission to assessment milestones.
- [README](README.md) provides installation, startup, and demo instructions.

## Architecture and implementation

FastAPI accepts HTML form submissions and renders Jinja templates. SQLite stores task details and status history. A unique task ID prevents duplicate records. A write transaction reads the current status, changes it, and records history together. Repeating the current status creates no history entry. The board independently filters by assignee and priority. The dashboard shows project-wide counts and the latest five created tasks.

The sample-data script creates 30 tasks across the four statuses, all three priorities, and three simulated assignees. A second run inserts zero duplicates and preserves edits. The app binds to localhost for a reproducible demonstration.

## AI-assisted work and review

The planning prompt asked Codex to write `intent.md` using the assignment's acceptance criteria, constraints, and scope. The follow-up request asked for help completing the project from start to finish. Codex drafted the specification and plan, built the app and tests, and ran verification. [Agent instructions](AGENTS.md) record the conventions used for implementation and testing.

One correction came from running the AI-generated UI in Chrome. The first browser run could submit the create and edit forms but timed out when Playwright looked up the status dropdown by the exact label **Status**. The initial template wrapped the dropdown inside the label. The revised template associates a separate label with the dropdown by ID, and the same adjustment was applied to the other select controls. The rerun found the controls by their exact labels and completed the workflow. A separate pytest run surfaced a deprecated test HTTP client, which was replaced. The clean-environment run passed without warnings.

## Verification results

| Check | Observed result |
| --- | --- |
| Automated suite on Python 3.12 | 15 passed in a fresh virtual environment. Coverage includes input validation, duplicate IDs, edits, status transitions, concurrent moves, filtering, dashboard counts, seed repeatability, and restart persistence. |
| Browser workflow | Chrome created and edited `TASK-101`, moved it from To Do through In Progress and In Review to Done, and showed three history entries. The combined Nina and High filter returned four cards. The board fit a 390-pixel viewport without horizontal overflow. |
| Independent data check | The demo was checked against SQLite queries separate from the pytest suite. Chrome and SQLite agreed on 31 tasks, 7 open High priority tasks, and status counts of 8 To Do, 8 In Progress, 7 In Review, and 8 Done. |
| Real server restart | After stopping and restarting Uvicorn with the same database, Chrome showed `TASK-101` in Done with all three history entries. |

## Evidence

| Screen | What it shows |
| --- | --- |
| [Seeded board](docs/evidence/board.png) | 30 simulated tasks across four columns. |
| [Task history](docs/evidence/task-history.png) | The final status and three dated changes for `TASK-101`. |
| [Dashboard](docs/evidence/dashboard.png) | Totals after the browser-created task was moved to Done. |

## Jira, GitHub, and submission status

The assessment is tracked in [TF-1](https://jelenaratkovicc47.atlassian.net/browse/TF-1). The issue link was provided before implementation began. The local history records planning (`acb7050`), application work (`b1da058`), and verification and CI setup (`3aa9fb2`). Jira milestone comments and transitions are awaiting authenticated Jira access.

The [GitHub Actions workflow](.github/workflows/ci.yml) installs the test dependencies and runs pytest on pushes and pull requests. The application was published to the [TaskFlow repository](https://github.com/jelenaratkovicc47-cell/taskflow). The hosted `test` job passed on commit `610f24e`, including dependency installation and the pytest step. [Passing GitHub Actions run](https://github.com/jelenaratkovicc47-cell/taskflow/actions/runs/44922878231)

## Known limitations and interview demo

This demo uses one SQLite file, fixed assignees, and a single project. Status changes use a dropdown. A team member can show the board, create a task, move it through review, and compare the dashboard with stored data. The SQLite uniqueness rule and status transaction provide two concrete decisions to explain in the interview.
