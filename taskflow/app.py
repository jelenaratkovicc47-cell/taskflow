import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import store


APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=APP_DIR / "templates")
templates.env.globals.update(assignees=store.ASSIGNEES, priorities=store.PRIORITIES, statuses=store.STATUSES)


def task_fields(
    title: Annotated[str, Form()] = "",
    description: Annotated[str, Form()] = "",
    assignee: Annotated[str, Form()] = "",
    priority: Annotated[str, Form()] = "",
) -> dict:
    return {"title": title.strip(), "description": description.strip(), "assignee": assignee, "priority": priority}


def validate_task(fields: dict) -> dict:
    errors = {
        field: f"Enter a {field}." for field in ("title", "description") if not fields[field]
    }
    if fields["assignee"] not in store.ASSIGNEES:
        errors["assignee"] = "Choose a simulated assignee."
    if fields["priority"] not in store.PRIORITIES:
        errors["priority"] = "Choose Low, Medium, or High."
    return errors


def page(request: Request, template: str, code: int = 200, **context):
    return templates.TemplateResponse(request=request, name=template, context=context, status_code=code)


def missing_task(request: Request, task_id: str):
    return page(request, "missing.html", 404, task_id=task_id)


def task_redirect(request: Request, task_id: str):
    return RedirectResponse(request.url_for("task_detail", task_id=task_id), status_code=303)


def create_app(path: Path | None = None) -> FastAPI:
    path = store.database_path() if path is None else path

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        store.initialize(path)
        yield

    app = FastAPI(title="TaskFlow", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

    @app.get("/")
    def board(request: Request, assignee: str = "", priority: str = ""):
        if (assignee and assignee not in store.ASSIGNEES) or (priority and priority not in store.PRIORITIES):
            return page(request, "board.html", 422, columns={}, filter_error="Choose a valid assignee and priority.")
        with store.connect(path) as database:
            tasks = store.list_tasks(database, assignee, priority)
        columns = {status: [] for status in store.STATUSES}
        for task in tasks:
            columns[task["status"]].append(task)
        return page(request, "board.html", columns=columns, assignee=assignee, priority=priority)

    @app.get("/tasks/new")
    def new_task(request: Request):
        return page(request, "form.html", values={}, errors={}, editing=False)

    @app.post("/tasks")
    def add_task(
        request: Request,
        fields: Annotated[dict, Depends(task_fields)],
        task_id: Annotated[str, Form()] = "",
    ):
        task_id = task_id.strip().upper()
        fields["task_id"] = task_id
        errors = validate_task(fields)
        if not re.fullmatch(r"TASK-[1-9][0-9]*", task_id):
            errors["task_id"] = "Enter an ID like TASK-101. Use a positive number without leading zeros."
        if errors:
            return page(request, "form.html", 422, values=fields, errors=errors, editing=False)
        with store.connect(path) as database:
            created = store.create_task(database, {**fields, "status": "To Do", "created_at": store.now_utc()})
        if not created:
            errors["task_id"] = f"{task_id} already exists. Choose a different ID."
            return page(request, "form.html", 409, values=fields, errors=errors, editing=False)
        return task_redirect(request, task_id)

    @app.get("/tasks/{task_id}")
    def task_detail(request: Request, task_id: str):
        with store.connect(path) as database:
            database.execute("BEGIN")
            task = store.get_task(database, task_id)
            if task is None:
                return missing_task(request, task_id)
            history = store.get_history(database, task_id)
        return page(request, "detail.html", task=task, history=history)

    @app.get("/tasks/{task_id}/edit")
    def edit_task(request: Request, task_id: str):
        with store.connect(path) as database:
            task = store.get_task(database, task_id)
        if task is None:
            return missing_task(request, task_id)
        return page(request, "form.html", values=dict(task), errors={}, editing=True)

    @app.post("/tasks/{task_id}/edit")
    def save_task(request: Request, task_id: str, fields: Annotated[dict, Depends(task_fields)]):
        fields["task_id"] = task_id
        errors = validate_task(fields)
        with store.connect(path) as database:
            if errors:
                if store.get_task(database, task_id) is None:
                    return missing_task(request, task_id)
                return page(request, "form.html", 422, values=fields, errors=errors, editing=True)
            if not store.update_task(database, fields):
                return missing_task(request, task_id)
        return task_redirect(request, task_id)

    @app.post("/tasks/{task_id}/status")
    def set_status(request: Request, task_id: str, status: Annotated[str, Form()] = ""):
        with store.connect(path) as database:
            if status not in store.STATUSES:
                database.execute("BEGIN")
                task = store.get_task(database, task_id)
                if task is None:
                    return missing_task(request, task_id)
                history = store.get_history(database, task_id)
                return page(request, "detail.html", 422, task=task, history=history, status_error="Choose a valid status.")
            if not store.change_status(database, task_id, status):
                return missing_task(request, task_id)
        return task_redirect(request, task_id)

    @app.get("/dashboard")
    def dashboard(request: Request):
        with store.connect(path) as database:
            tasks = store.list_tasks(database)
        counts = dict.fromkeys(store.STATUSES, 0)
        open_by_assignee = dict.fromkeys(store.ASSIGNEES, 0)
        high_open = 0
        for task in tasks:
            counts[task["status"]] += 1
            if task["status"] != "Done":
                open_by_assignee[task["assignee"]] += 1
                high_open += task["priority"] == "High"

        total = len(tasks)
        done = counts["Done"]
        return page(
            request, "dashboard.html",
            counts=counts, total=total, high_open=high_open, recent=tasks[:5],
            active=counts["In Progress"] + counts["In Review"],
            completion=round(100 * done / total) if total else 0,
            open_by_assignee=open_by_assignee,
        )

    return app
