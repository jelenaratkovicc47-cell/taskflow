import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from taskflow.app import create_app
from taskflow.seed import seed


STATUSES = ("To Do", "In Progress", "In Review", "Done")
TASK = {
    "task_id": "TASK-101",
    "title": "Review onboarding",
    "description": "Check the handoff from design to engineering.",
    "assignee": "Maya",
    "priority": "High",
}


@pytest.fixture
def database(tmp_path: Path):
    return tmp_path / "test.db"


@pytest.fixture
def client(database: Path):
    with TestClient(create_app(database)) as browser:
        yield browser


def html(response):
    return BeautifulSoup(response.text, "html.parser")


def board_tasks(response):
    return {
        column["data-status"]: [card.small.get_text(strip=True) for card in column.select(".card")]
        for column in html(response).select("[data-status]")
    }


def add_task(client, **fields):
    response = client.post("/tasks", data={**TASK, **fields}, follow_redirects=False)
    assert response.status_code == 303
    return response.headers["location"]


def test_create_retrieve_and_edit(client):
    assert client.get("/tasks/new").status_code == 200
    location = add_task(client, task_id=" task-101 ", title="  Review onboarding  ")
    assert location.endswith("/tasks/TASK-101")
    page = html(client.get(location))
    assert page.h1.get_text(strip=True) == TASK["title"]
    assert page.select_one(".description").get_text(strip=True) == TASK["description"]
    assert page.select_one('[name="status"] [selected]').get_text(strip=True) == "To Do"
    assert datetime.fromisoformat(page.time["datetime"]).utcoffset() == timedelta(0)
    assert board_tasks(client.get("/")) == {"To Do": ["TASK-101"], "In Progress": [], "In Review": [], "Done": []}

    edit = html(client.get(f"{location}/edit"))
    assert edit.select_one('[name="title"]')["value"] == TASK["title"]
    assert edit.select_one('[name="task_id"]') is None
    edit_fields = {"title": "Review new onboarding", "description": "Verify new copy.", "assignee": "Nina", "priority": "Low"}
    response = client.post(f"{location}/edit", data=edit_fields, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == location
    saved = html(client.get(location))
    assert saved.h1.get_text(strip=True) == edit_fields["title"]
    assert saved.select_one(".description").get_text(strip=True) == edit_fields["description"]
    assert [value.get_text(strip=True) for value in saved.select(".facts dd")][:2] == ["Nina", "Low"]
    assert saved.time["datetime"] == page.time["datetime"]
    assert saved.select(".history tbody tr") == []


@pytest.mark.parametrize(
    ("field", "value"),
    [("task_id", "TASK-001"), ("title", "  "), ("description", ""), ("assignee", "Sam"), ("priority", "Urgent")],
)
def test_invalid_task_fields(client, field, value):
    response = client.post("/tasks", data={**TASK, field: value})
    assert response.status_code == 422
    assert html(response).select_one(f"#{field}-error")
    assert all(not tasks for tasks in board_tasks(client.get("/")).values())


def test_missing_fields_preserve_valid_input(client):
    response = client.post("/tasks", data={"title": TASK["title"]})
    assert response.status_code == 422
    page = html(response)
    assert len(page.select("[aria-invalid=true]")) == 4
    assert page.select_one('[name="title"]')["value"] == TASK["title"]


def test_duplicate_id_keeps_original(client):
    add_task(client)
    duplicate = client.post("/tasks", data={**TASK, "task_id": "task-101", "title": "Different title"})
    assert duplicate.status_code == 409
    assert "TASK-101 already exists" in html(duplicate).select_one("#task_id-error").get_text(strip=True)
    assert html(client.get("/tasks/TASK-101")).h1.get_text(strip=True) == TASK["title"]
    assert board_tasks(client.get("/"))["To Do"] == ["TASK-101"]


def test_invalid_edit_keeps_original(client):
    location = add_task(client)
    invalid = client.post(f"{location}/edit", data={**TASK, "title": "New title", "assignee": "Sam"})
    assert invalid.status_code == 422
    assert html(invalid).select_one("#assignee-error")
    assert html(client.get(location)).h1.get_text(strip=True) == TASK["title"]


def test_status_history_and_move_back(client):
    location = add_task(client)
    for status in ("In Review", "To Do", "To Do"):
        response = client.post(f"{location}/status", data={"status": status}, follow_redirects=False)
        assert response.status_code == 303
        assert board_tasks(client.get("/"))[status] == ["TASK-101"]
    invalid = client.post(f"{location}/status", data={"status": "Blocked"})
    assert invalid.status_code == 422
    assert html(invalid).select_one("#status-error")
    rows = html(client.get(location)).select(".history tbody tr")
    assert [[cell.get_text(strip=True) for cell in row.select("td")[:2]] for row in rows] == [
        ["In Review", "To Do"], ["To Do", "In Review"],
    ]
    assert all(datetime.fromisoformat(row.time["datetime"]).utcoffset() == timedelta(0) for row in rows)


def test_unknown_task_returns_404(client):
    path = "/tasks/TASK-999"
    assert client.get(path).status_code == 404
    assert client.get(f"{path}/edit").status_code == 404
    assert client.post(f"{path}/edit", data=TASK).status_code == 404
    assert client.post(f"{path}/status", data={"status": "Done"}).status_code == 404


def test_dashboard_totals_and_filters(client):
    add_task(client)
    done = add_task(client, task_id="TASK-102", assignee="Nina")
    client.post(f"{done}/status", data={"status": "Done"})
    add_task(client, task_id="TASK-103", priority="Low")
    add_task(client, task_id="TASK-104", assignee="Leo", priority="Medium")
    add_task(client, task_id="TASK-105", assignee="Nina", priority="Low")
    add_task(client, task_id="TASK-106", assignee="Nina", priority="Medium")

    assignee_only = board_tasks(client.get("/", params={"assignee": "Maya"}))
    assert assignee_only["To Do"] == ["TASK-103", "TASK-101"]
    priorities_only = board_tasks(client.get("/", params={"priority": "High"}))
    assert priorities_only["To Do"] == ["TASK-101"]
    assert priorities_only["Done"] == ["TASK-102"]
    both = board_tasks(client.get("/", params={"assignee": "Nina", "priority": "High"}))
    assert both == {"To Do": [], "In Progress": [], "In Review": [], "Done": ["TASK-102"]}
    assert client.get("/", params={"assignee": "Sam"}).status_code == 422

    client.post("/tasks/TASK-104/status", data={"status": "In Progress"})
    client.post("/tasks/TASK-105/status", data={"status": "In Review"})
    dashboard = html(client.get("/dashboard"))
    totals = {item.dt.get_text(strip=True): int(item.dd.get_text(strip=True)) for item in dashboard.select(".metrics > div")}
    assert totals == {"Total tasks": 6, "Active work": 2, "Open high priority": 1, "Completed": 1}
    counts = {item.dt.get_text(strip=True): int(item.dd.get_text(strip=True)) for item in dashboard.select(".workflow-counts > div")}
    assert counts == {"To Do": 3, "In Progress": 1, "In Review": 1, "Done": 1}
    assert dashboard.select_one(".completion-ring").get_text(strip=True) == "17%"
    workload = {
        link.select_one(".workload-name").get_text(strip=True): link.select_one(".workload-count").get_text(strip=True)
        for link in dashboard.select(".workload-list a")
    }
    assert workload == {
        "Maya": "2 open", "Leo": "1 open", "Nina": "2 open",
        "Avery": "0 open", "Omar": "0 open", "Priya": "0 open",
    }
    assert [link["href"].split("?")[-1] for link in dashboard.select(".workload-list a")] == [
        "assignee=Maya", "assignee=Leo", "assignee=Nina", "assignee=Avery", "assignee=Omar", "assignee=Priya",
    ]
    links = dashboard.select("tbody a")
    assert [link["href"].rsplit("/", 1)[-1] for link in links] == [f"TASK-{number}" for number in range(106, 101, -1)]


def test_empty_dashboard_shows_zero_activity(client):
    dashboard = html(client.get("/dashboard"))
    assert [int(value.get_text(strip=True)) for value in dashboard.select(".metrics dd")] == [0, 0, 0, 0]
    assert dashboard.select_one(".completion-ring").get_text(strip=True) == "0%"
    assert dashboard.select_one(".dashboard-empty a").get_text(strip=True) == "Create a task"


def test_seed_is_repeatable_and_preserves_edits(database):
    assert seed(database) == 60
    with TestClient(create_app(database)) as browser:
        response = browser.post("/tasks/TASK-1001/edit", data={**TASK, "title": "Keep this edit"})
        assert html(response).h1.get_text(strip=True) == "Keep this edit"
        new_task = html(browser.get("/tasks/new"))
        assignees = [option.get_text(strip=True) for option in new_task.select('[name="assignee"] option')[1:]]
        assert assignees == ["Maya", "Leo", "Nina", "Avery", "Omar", "Priya"]
        priya_tasks = board_tasks(browser.get("/", params={"assignee": "Priya"}))
        assert sum(len(tasks) for tasks in priya_tasks.values()) == 10
    assert seed(database) == 0
    with sqlite3.connect(database) as connection:
        rows = connection.execute("SELECT task_id, status, assignee, priority, title FROM tasks").fetchall()
    assert len(rows) == 60
    assert {row[1] for row in rows} == set(STATUSES)
    assert {row[2] for row in rows} == {"Maya", "Leo", "Nina", "Avery", "Omar", "Priya"}
    assert {row[3] for row in rows} == {"Low", "Medium", "High"}
    assert next(row[4] for row in rows if row[0] == "TASK-1001") == "Keep this edit"


def test_task_and_history_survive_restart(database):
    with TestClient(create_app(database)) as before:
        location = add_task(before)
        for status in ("In Progress", "In Review", "Done"):
            assert before.post(f"{location}/status", data={"status": status}).status_code == 200
    with TestClient(create_app(database)) as after:
        assert board_tasks(after.get("/"))["Done"] == ["TASK-101"]
        rows = html(after.get(location)).select(".history tbody tr")
        assert [row.select("td")[1].get_text(strip=True) for row in rows] == ["Done", "In Review", "In Progress"]


def test_simultaneous_changes_form_a_contiguous_history(client):
    location = add_task(client)
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(
            lambda status: client.post(f"{location}/status", data={"status": status}, follow_redirects=False),
            ("In Progress", "In Review"),
        ))
    assert [response.status_code for response in responses] == [303, 303]
    page = html(client.get(location))
    latest, first = [[cell.get_text(strip=True) for cell in row.select("td")[:2]] for row in page.select(".history tbody tr")]
    assert first[0] == "To Do"
    assert first[1] == latest[0]
    assert {first[1], latest[1]} == {"In Progress", "In Review"}
    assert page.select_one('[name="status"] [selected]').get_text(strip=True) == latest[1]
