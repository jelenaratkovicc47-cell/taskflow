# Working on TaskFlow

- Read `intent.md`, `spec.md`, and `plan.md` before changing the app. Record agreed behavior changes in the spec and assessment issue.
- Use Python, FastAPI, SQLite, simple HTML, pytest, and GitHub Actions. Use simulated data for demos, tests, and screenshots.
- Keep task validation consistent across create and edit. Enforce unique task IDs in SQLite and save status and history in one transaction.
- Run pytest after changes. Tests should use their own temporary database. Verify the main task flow in the browser before claiming it works end to end.
- Record actual Jira updates, commit references, verification results, and one AI-assisted change with its review and correction. Report only CI runs and screenshots that were captured.
