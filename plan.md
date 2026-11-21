# TaskFlow delivery plan

Local planning is underway. The designated Jira project is TF, board 2. The Story or Epic still needs confirmation. [TF assessment board](https://jelenaratkovicc47.atlassian.net/jira/software/projects/TF/boards/2)

| Milestone | Tasks | Evidence to record in Jira |
| --- | --- | --- |
| 1. Assessment setup and planning | Create or confirm the Story or Epic on the designated board before coding. Review `intent.md`, `spec.md`, and this plan. Commit the planning documents and add an AI agent instruction file before implementation. | Problem, objective, requirements, assumptions, risks, acceptance criteria, and links to the planning documents. |
| 2. Core task flow | Create FastAPI routes, SQLite storage, and task forms. Build and check creation, retrieval, edits, duplicate rejection, and status history. Review the changes and commit the working flow. | What works, any changed decisions or blockers, and commit or PR links. |
| 3. Board and dashboard | Add the four board columns, filters, summary counts, recent tasks, and the sample-data script. Run the seeded board in the browser and commit the feature set. | Summary of filters, counts, demo data, and remaining work. |
| 4. Verification | Write pytest coverage for the checks in the spec and a full create-to-Done scenario. Independently compare browser and database results against a small set with known counts. Review failures, fix defects, and record one real AI prompt, output, verification, and improvement. | Commands and results, defects found, fixes, and browser evidence. |
| 5. CI and reproducible startup | Create a push-triggered GitHub Actions workflow. Publish to the confirmed repository, verify the actual CI result, and follow the README from a clean environment. | Passing run link and startup instructions. |
| 6. Submission and interview | Write the final report with screenshots, links, AI review, challenges, and limitations. Check the submission package, update Jira, and prepare to demo and explain the work. | Repository, report, CI run, evidence, and final status after submission and verification. |

Use the workflow states available on the assessment board. Post updates as each milestone happens. Capture evidence at the time it is produced.

## Risks and checks

- A repeated or concurrent submission can create inconsistent data. Enforce unique IDs in SQLite and save the task status and history together.
- Filtered board cards and dashboard totals can disagree with the stored data. Verify both against a fixture with known results, including a High priority task already in Done.
- Local test results can differ from CI. Document a supported Python version and use the same test command locally and in GitHub Actions.
- Access to the assessment Jira project or GitHub repository can delay evidence collection. Confirm access early and link verified results as each milestone completes.

## Jira issue draft

**Title** · Build TaskFlow - Simulated Project Management System

**Type** · Story or Epic, according to the assessment board

**Business problem and objective** · A small software team tracks tasks in messages and spreadsheets and struggles to see ownership and progress. Give the project manager, developers, and QA a shared board to track and prioritize work.

**Functional requirements** · Create, edit, and view tasks. Reject duplicate IDs and explain invalid input. Track To Do, In Progress, In Review, and Done with dated transition history. Filter the board by assignee and priority. Show dashboard counts and recent tasks. Seed at least 30 tasks across three simulated assignees.

**Non-functional requirements and assumptions** · Run locally using Python, FastAPI, SQLite, and simple HTML. Use simulated data, one project, fixed assignees, free services, and no login. Allow any transition between distinct statuses. Preserve tasks and history on restart and verify behavior with pytest and GitHub Actions. Use Jira to track the assessment.

**Acceptance criteria** · A valid task appears on the board and edits persist. Invalid and duplicate submissions return useful errors. A status change moves the task and adds a dated history entry. Dashboard totals and filters match stored data. The seed script creates varied tasks, and tasks and history survive restart. The README works from a clean environment, CI passes, and this issue links to the repository, CI run, report, and progress updates.

**Deliverables and implementation plan** · Submit the working app, planning documents, AI instructions, tests, CI workflow and run, README, and final report with evidence. Track implementation, verification, delivery, and submission using the milestones above. Watch for duplicate IDs, inconsistent status history, mismatched counts, and CI differences.
