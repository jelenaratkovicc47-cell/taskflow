# TaskFlow assessment report

## Problem and delivery

A small software team needed one place to see task ownership, priority, and progress. TaskFlow provides a board for the project manager, developers, and QA. The current version runs locally with one simulated project and six assignees.

- [Intent](intent.md) defines the business goal, scope, and success criteria.
- [Specification](spec.md) defines behavior, the data model, and verification checks.
- [Delivery plan](plan.md) maps implementation, testing, CI, and submission to assessment milestones.
- [README](README.md) provides installation, startup, and demo instructions.

## Architecture and implementation

FastAPI accepts HTML form submissions and renders Jinja templates. SQLite stores task details and status history. A unique task ID prevents duplicate records. A write transaction reads the current status, changes it, and records history together. Repeating the current status creates no history entry. The board independently filters by assignee and priority. The dashboard shows project-wide counts, active work, completion percentage, open workload by assignee, and the five newest tasks.

The sample-data script creates 60 tasks across the four statuses, all three priorities, and six simulated assignees. Running the expanded seed against the original demo database added 30 tasks and preserved the existing records. A second run added zero duplicates. The app binds to localhost for a reproducible demonstration.

## AI-assisted work and review

The planning prompt asked Codex to write `intent.md` using the assignment's acceptance criteria, constraints, and scope. The follow-up request asked for help completing the project from start to finish. Codex drafted the specification and plan, built the app and tests, and ran verification. [Agent instructions](AGENTS.md) record the conventions used for implementation and testing.

One correction came from running the AI-generated UI in Chrome. The first browser run could submit the create and edit forms but timed out when Playwright looked up the status dropdown by the exact label **Status**. The initial template wrapped the dropdown inside the label. The revised template associates a separate label with the dropdown by ID, and the same adjustment was applied to the other select controls. The rerun found the controls by their exact labels and completed the workflow. A separate pytest run surfaced a deprecated test HTTP client, which was replaced. The clean-environment run passed without warnings.

## Verification results

| Check | Observed result |
| --- | --- |
| Automated suite on Python 3.12 | 16 tests passed after the redesign and seed expansion. Coverage includes input validation, duplicate IDs, edits, status transitions, concurrent moves, filtering, dashboard totals, per-assignee workload, empty-dashboard behavior, seed repeatability, and restart persistence. The original clean-environment assessment run passed all 15 tests in the suite at that time. |
| Browser workflow on November 21 | Chrome created and edited `TASK-101`, moved it from To Do through In Progress and In Review to Done, and showed three history entries. The combined Nina and High filter returned four cards. The board fit a 390-pixel viewport without horizontal overflow. |
| Independent data check on November 21 | The original 30-task demo was checked against SQLite queries separate from the pytest suite. After the browser added `TASK-101`, Chrome and SQLite agreed on 31 tasks, 7 open High priority tasks, and status counts of 8 To Do, 8 In Progress, 7 In Review, and 8 Done. |
| Real server restart on November 21 | After stopping and restarting Uvicorn with the same database, Chrome showed `TASK-101` in Done with all three history entries. |
| Updated demo on November 22 | Chrome showed 60 tasks and six assignees. The new team members appeared in the workload panel and task form, and the Priya filter returned ten tasks. |

## Online preview

GitHub Pages serves a read-only snapshot with 60 sample tasks and six assignees. Visitors can view the dashboard and browse the sample board. The local FastAPI app starts from the README and provides task creation, editing, status changes, and SQLite persistence. [Open the TaskFlow preview](https://jelenaratkovicc47-cell.github.io/taskflow/)

## Evidence

These screenshots show the original demo captured on November 21, before the redesign and expansion to 60 sample tasks.

| Screen | What it shows |
| --- | --- |
| [Seeded board](docs/evidence/board.png) | 30 simulated tasks across four columns. |
| [Task history](docs/evidence/task-history.png) | The final status and three dated changes for `TASK-101`. |
| [Dashboard](docs/evidence/dashboard.png) | Totals after the browser-created task was moved to Done. |

## Jira, GitHub, and submission status

TF-1 was created before implementation began. The six child items track the work from planning through delivery. The original implementation commit covers task management, status history, the board, the dashboard, and SQLite storage, so several items share that commit. [Assessment epic TF-1](https://jelenaratkovicc47.atlassian.net/browse/TF-1) · [Original implementation commit](https://github.com/jelenaratkovicc47-cell/taskflow/commit/b1da058)

| Jira work item | Published evidence |
| --- | --- |
| [TF-1](https://jelenaratkovicc47.atlassian.net/browse/TF-1) · Deliver TaskFlow | [Repository](https://github.com/jelenaratkovicc47-cell/taskflow), [public dashboard](https://jelenaratkovicc47-cell.github.io/taskflow/), and [passing CI run](https://github.com/jelenaratkovicc47-cell/taskflow/actions/runs/45039152830) |
| [TF-2](https://jelenaratkovicc47.atlassian.net/browse/TF-2) · Plan the project | [Original intent, specification, and plan](https://github.com/jelenaratkovicc47-cell/taskflow/commit/acb7050) |
| [TF-3](https://jelenaratkovicc47.atlassian.net/browse/TF-3) · Create and edit tasks | [Task routes and form validation](https://github.com/jelenaratkovicc47-cell/taskflow/blob/b1da058/taskflow/app.py) |
| [TF-4](https://jelenaratkovicc47.atlassian.net/browse/TF-4) · Track status and history | [SQLite status transaction](https://github.com/jelenaratkovicc47-cell/taskflow/blob/b1da058/taskflow/store.py) and [history screenshot](docs/evidence/task-history.png) |
| [TF-5](https://jelenaratkovicc47.atlassian.net/browse/TF-5) · Build the board and dashboard | [Public dashboard and sample board](https://jelenaratkovicc47-cell.github.io/taskflow/) and [dashboard redesign commit](https://github.com/jelenaratkovicc47-cell/taskflow/commit/7b19cdb) |
| [TF-6](https://jelenaratkovicc47.atlassian.net/browse/TF-6) · Seed tasks and verify persistence | [Expanded sample-data script](https://github.com/jelenaratkovicc47-cell/taskflow/blob/7b19cdb/taskflow/seed.py) and [restart verification](#verification-results) |
| [TF-7](https://jelenaratkovicc47.atlassian.net/browse/TF-7) · Test and document delivery | [Test and CI setup](https://github.com/jelenaratkovicc47-cell/taskflow/commit/3aa9fb2), [passing CI run](https://github.com/jelenaratkovicc47-cell/taskflow/actions/runs/45039152830), and [README](README.md) |

The GitHub Actions workflow installs the test dependencies and runs pytest on pushes and pull requests. The hosted `test` job passed on commit `f635480`, which includes the dashboard redesign, expanded sample data, and public preview. [GitHub Actions workflow](.github/workflows/ci.yml) · [TaskFlow repository](https://github.com/jelenaratkovicc47-cell/taskflow) · [Passing GitHub Actions run](https://github.com/jelenaratkovicc47-cell/taskflow/actions/runs/45037969015)

## Known limitations and interview demo

This demo uses one SQLite file, fixed assignees, and a single project. Status changes use a dropdown. A team member can show the board, create a task, move it through review, and compare the dashboard with stored data. The SQLite uniqueness rule and status transaction provide two concrete decisions to explain in the interview.
