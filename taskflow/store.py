import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


STATUSES = ("To Do", "In Progress", "In Review", "Done")
PRIORITIES = ("Low", "Medium", "High")
ASSIGNEES = ("Maya", "Leo", "Nina", "Avery", "Omar", "Priya")


def database_path() -> Path:
    return Path(os.environ.get("TASKFLOW_DB", "taskflow.db"))


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


@contextmanager
def connect(path: Path):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            yield connection
    finally:
        connection.close()


def initialize(path: Path) -> None:
    with connect(path) as database:
        database.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                assignee TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY,
                task_id TEXT NOT NULL REFERENCES tasks(task_id),
                old_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                changed_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS status_history_task
                ON status_history(task_id, id DESC);
            """
        )


def create_task(database: sqlite3.Connection, task: dict) -> bool:
    result = database.execute(
        """INSERT INTO tasks (task_id, title, description, assignee, priority, status, created_at)
           VALUES (:task_id, :title, :description, :assignee, :priority, :status, :created_at)
           ON CONFLICT (task_id) DO NOTHING""",
        task,
    )
    return result.rowcount == 1


def get_task(database: sqlite3.Connection, task_id: str):
    return database.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()


def update_task(database: sqlite3.Connection, task: dict) -> bool:
    result = database.execute(
        """UPDATE tasks SET title = :title, description = :description,
           assignee = :assignee, priority = :priority WHERE task_id = :task_id""",
        task,
    )
    return result.rowcount == 1


def change_status(database: sqlite3.Connection, task_id: str, new_status: str) -> bool:
    database.execute("BEGIN IMMEDIATE")
    task = get_task(database, task_id)
    if task is None:
        return False
    if task["status"] != new_status:
        database.execute("UPDATE tasks SET status = ? WHERE task_id = ?", (new_status, task_id))
        database.execute(
            """INSERT INTO status_history (task_id, old_status, new_status, changed_at)
               VALUES (?, ?, ?, ?)""",
            (task_id, task["status"], new_status, now_utc()),
        )
    return True


def get_history(database: sqlite3.Connection, task_id: str):
    return database.execute(
        "SELECT * FROM status_history WHERE task_id = ? ORDER BY id DESC", (task_id,)
    ).fetchall()


def list_tasks(database: sqlite3.Connection, assignee: str = "", priority: str = ""):
    return database.execute(
        """SELECT * FROM tasks
           WHERE (:assignee = '' OR assignee = :assignee)
             AND (:priority = '' OR priority = :priority)
           ORDER BY created_at DESC, task_id DESC""",
        {"assignee": assignee, "priority": priority},
    ).fetchall()
