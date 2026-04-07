# MzansiBuilds — Architecture & Project Documentation

## 1. Project Overview

MzansiBuilds is a developer community platform built for South African developers
to share what they are building publicly, track progress, collaborate with peers,
and celebrate completed projects.

**Problem Statement:**
South African developers often build in isolation. There is no dedicated space for
local developers to share work-in-progress projects, find collaborators, or get
community feedback during the build process — not just after shipping.

**Solution:**
A web platform where developers can post projects from day one, update progress
through defined stages, and engage with other builders through comments and
collaboration requests.

---

## 2. System Architecture

### Pattern
**MVC (Model-View-Controller)** implemented using Flask's Blueprint system:

```
Models     →  SQLAlchemy ORM classes (User, Project, Milestone, Comment)
Views      →  Jinja2 HTML templates (templates/)
Controller →  Flask Blueprint route handlers (routes/)
```

### Request Lifecycle

```
Browser Request
      ↓
Flask Router (run.py → create_app())
      ↓
Blueprint Route Handler (routes/*.py)
      ↓
Model / Database Query (models/*.py via SQLAlchemy)
      ↓
Jinja2 Template Render (templates/*.html)
      ↓
HTML Response to Browser
```

### Database Schema

```
User
  id, username, name, bio, password_hash, joined_at

Project
  id, user_id (FK→User), title, description, stage,
  support_needed, tech_tags, is_completed, created_at, updated_at

Milestone
  id, project_id (FK→Project), text, created_at

Comment
  id, project_id (FK→Project), user_id (FK→User), text, created_at

collab_hands (association table)
  user_id (FK→User), project_id (FK→Project)
```

---

## 3. Technology Decisions

| Decision | Choice | Reason |
|---|---|---|
| Language | Python | Strong ecosystem, readable syntax, widely used in SA industry |
| Framework | Flask | Lightweight, gives full control over architecture — avoids magic |
| ORM | SQLAlchemy | Industry standard, clean model definitions, migration-ready |
| Auth | Flask-Login + Werkzeug | Proven, minimal, handles session management securely |
| Database | SQLite | Zero-config for development; easily swapped to PostgreSQL for production |
| Templating | Jinja2 | Server-side rendering — no JavaScript framework overhead |
| Testing | pytest | Clean fixture system, readable assertions |
| CI/CD | GitHub Actions | Native to GitHub, free for public repos, triggers on every push |

---

## 4. Security Approach (Secure By Design)

Security was considered from the start, not added afterwards:

- **Password Hashing** — Werkzeug's `generate_password_hash` (PBKDF2-SHA256) used on registration. Plaintext passwords are never stored.
- **Session Management** — Flask-Login handles secure server-side sessions. Login required decorators protect every authenticated route.
- **Ownership Checks** — Every edit, delete, milestone, and stage update route verifies `project.user_id == current_user.id` before proceeding. Returns HTTP 403 on violation.
- **CSRF Awareness** — Flask-WTF is included in requirements for CSRF token support on forms.
- **No Raw SQL** — All database queries use SQLAlchemy ORM, preventing SQL injection.
- **Environment Variables** — Secret key and config loaded from `.env` (excluded from version control via `.gitignore`).

---

## 5. Development Approach

### Methodology
Feature-by-feature development following the user journey defined in the SRS:

1. Account management (auth) → base layout and navigation
2. Project creation and management
3. Live feed and collaboration features
4. Milestone tracking
5. Celebration wall
6. Developer profiles
7. Tests, CI/CD, documentation

### Branching Strategy
- `main` — production-ready code only
- Feature branches should follow: `feature/feature-name`
- Every push to `main` triggers the CI pipeline via GitHub Actions

---

## 6. UML Diagrams

See `use_case_diagram.puml` in this folder.

To render the diagram:
- Paste the contents into [planttext.com](https://www.planttext.com)
- Or install the PlantUML VS Code extension

---

## 7. AI Usage Statement (Ethical Use of AI)

Claude (Anthropic) was used as a development companion during this project.

**What AI assisted with:**
- Generating boilerplate Flask project structure and model definitions
- Suggesting CSS patterns for the design system
- Writing initial test scaffolding

**What reflects own thinking and decisions:**
- The decision to use Flask over Django — chosen for its explicit, non-magic architecture which suits a portfolio project where understanding each layer matters
- The MVC blueprint structure — decided to separate concerns into models/routes/templates rather than a flat single-file approach
- The choice to use server-side rendering (Jinja2) rather than a JavaScript frontend framework — a deliberate decision to keep the stack simple and Python-focused
- Identifying that the `.env` file and `instance/` folder needed to be in `.gitignore` before pushing to a public repo
- Removing AI-generated emoji from the README after recognising it looked inauthentic
- Writing the test cases with specific assertions that reflect understanding of the business logic (e.g. idempotent hand-raises, ownership access control)
- All debugging and error resolution during local setup (execution policy, instance folder, git branch issues) was handled independently

**Approach to AI use:**
AI was used to accelerate delivery, not to replace understanding. Every file generated was read, understood, and where necessary modified before being committed. The goal was to use AI as a senior pair-programming partner — not as a replacement for thinking.
