# MzansiBuilds

> **Build in public. Grow together.**
> A developer community platform for South African builders — share your projects, track milestones, collaborate, and celebrate shipping.

Built for the **Derivco Code Skills Challenge**.

---

## Features

| Feature | Description |
|---|---|
| Account Management | Register, login, logout with secure password hashing |
| Project Entries | Create projects with stage, support needed, and tech stack |
| Live Feed | See what other developers are building in real-time |
| Collaboration | Raise or lower your hand to request collaboration on any project |
| Comments | Comment on any project in the feed |
| Milestones | Log progress milestones for your own projects |
| Stage Updates | Move your project through Ideation, Planning, In Progress, Testing, Deployed |
| Celebration Wall | Completed projects are showcased on the public wall |
| Developer Profiles | Public profiles with stats and project history |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web Framework | Flask 3.0 |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login + Werkzeug password hashing |
| Database | SQLite (development) |
| Templates | Jinja2 (server-side rendering) |
| Testing | pytest + pytest-flask |
| CI/CD | GitHub Actions |
| Styling | Vanilla CSS (custom design system — green/black/white) |

---

## Project Structure

```
mzansibuilds/
├── run.py                        # Entry point
├── __init__.py                   # App factory + seed data
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development and test dependencies
├── pytest.ini                    # Test configuration
├── SECURITY.md                   # Security policy and measures
│
├── models/
│   ├── user.py                   # User model + Flask-Login integration
│   ├── project.py                # Project model + collaboration many-to-many
│   ├── milestone.py              # Milestone model
│   └── comment.py                # Comment model
│
├── routes/
│   ├── auth.py                   # Login, register, logout
│   ├── feed.py                   # Live feed
│   ├── projects.py               # CRUD, milestones, comments, collaboration
│   ├── wall.py                   # Celebration wall
│   └── profile.py                # Developer profiles
│
├── templates/
│   ├── base.html                 # Base layout with navigation
│   ├── feed.html
│   ├── wall.html
│   ├── profile.html
│   ├── edit_profile.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── projects/
│       ├── new.html
│       ├── edit.html
│       ├── detail.html
│       └── my_projects.html
│
├── static/
│   ├── css/main.css              # Full design system
│   └── js/main.js               # UI interactivity
│
├── tests/
│   ├── conftest.py               # Shared pytest fixtures
│   ├── test_models_user.py       # User model unit tests
│   ├── test_models_project.py    # Project model unit tests
│   ├── test_routes_auth.py       # Auth route integration tests
│   └── test_routes_projects.py   # Project route integration tests
│
├── docs/
│   ├── ARCHITECTURE.md           # System architecture and design decisions
│   ├── use_case_diagram.puml     # UML Use Case diagram source
│   └── use_case_diagram.png      # Rendered UML diagram
│
└── .github/
    └── workflows/
        └── ci.yml                # GitHub Actions CI pipeline
```

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Jashin1802/mzansibuilds.git
cd mzansibuilds
```

### 2. Create and activate a virtual environment
```bash
# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Create the instance folder
```bash
mkdir instance
```

### 5. Run the app
```bash
python run.py
```

Open your browser at **http://localhost:5000**

---

## Running Tests

```bash
pytest -v
```

Tests use an isolated in-memory SQLite database and never affect the development database.

---

## Demo Accounts

The app seeds demo data on first run:

| Username | Password |
|---|---|
| `sipho_dev` | `password` |
| `amahle_codes` | `password` |
| `kagiso_builds` | `password` |

---

## CI/CD

Every push to `main` triggers the GitHub Actions pipeline which:
- Sets up Python 3.11
- Installs all dependencies
- Creates the instance directory
- Runs the full test suite with pytest

See `.github/workflows/ci.yml` for configuration.

---

## Security

See `SECURITY.md` for the full security policy. Key measures include:

- Passwords hashed using PBKDF2-SHA256 — never stored in plaintext
- All authenticated routes protected with `@login_required`
- Ownership verified before any project mutation (HTTP 403 on violation)
- SQLAlchemy ORM used throughout — no raw SQL
- Secret key loaded from `.env` which is excluded from version control

---

## Documentation

- Architecture and design decisions: `docs/ARCHITECTURE.md`
- UML Use Case diagram: `docs/use_case_diagram.png`
- Security policy: `SECURITY.md`
- AI usage statement: `docs/ARCHITECTURE.md` section 7

---

*Built for the Derivco Code Skills Challenge*
