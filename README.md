# TaskFlow

TaskFlow is a local project board for one simulated software team. Create and edit tasks, move them through four statuses, and review project totals and task history.

## Start locally

Install Python 3.12, then run these commands from the repository root.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m taskflow.seed
python -m uvicorn taskflow.app:create_app --factory --host 127.0.0.1 --port 8000
```

On Windows PowerShell, use `py -3.12 -m venv .venv` and `.venv\Scripts\Activate.ps1` for the first two commands.

Open `http://127.0.0.1:8000/`. The sample script adds 60 tasks across six simulated teammates. It skips IDs already present, so running it again adds any missing sample tasks and preserves edits. Skip the seed command for an empty board.

Tasks and status history persist in `taskflow.db` in the current directory. To use a different file, set `TASKFLOW_DB` to its path in the shell before seeding or starting the app. The file's parent directory must exist. This is a local demo with no login.

## Try the workflow

1. Choose **New task** and enter an available ID such as `TASK-101`, a title, a description, an assignee, and a priority.
2. Open the task, edit its details, and move it from **To Do** to **In Review**.
3. Check the status history on the task page. Return to the board and filter by the task's assignee and priority.
4. Open **Dashboard** and check the status totals, open high-priority count, and recent tasks.
5. Stop the server and run the same startup command again. Open the task and check that its history is still present.

## Run the tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest
```

The tests use temporary SQLite files. The GitHub Actions workflow runs the same suite on pushes and pull requests.

## Assessment

- [Intent](intent.md), [specification](spec.md), and [delivery plan](plan.md)
- [Assessment issue TF-1](https://jelenaratkovicc47.atlassian.net/browse/TF-1)
- [Assessment report and browser evidence](final-report.md)
