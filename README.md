# MzansiBuilds 🌍

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
| Collaboration | Raise/lower your hand to request collaboration on any project |
| Comments | Comment on any project in the feed |
| Milestones | Log progress milestones for your own projects |
| Stage Updates | Move your project through Ideation → Planning → In Progress → Testing → Deployed |
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
| Styling | Vanilla CSS (custom design system — green/black/white) |
| Fonts | Space Grotesk + JetBrains Mono (Google Fonts) |

---

## Project Structure

```
mzansibuilds/
├── run.py                  # Entry point
├── __init__.py             # App factory + seed data
├── requirements.txt
├── .env                    # Environment variables (not committed)
├── .gitignore
│
├── models/
│   ├── user.py             # User model + Flask-Login integration
│   ├── project.py          # Project model + collab many-to-many
│   ├── milestone.py        # Milestone model
│   └── comment.py          # Comment model
│
├── routes/
│   ├── auth.py             # Login, register, logout
│   ├── feed.py             # Live feed
│   ├── projects.py         # CRUD + milestones + comments + collab
│   ├── wall.py             # Celebration wall
│   └── profile.py          # Developer profiles
│
├── templates/
│   ├── base.html           # Base layout with nav
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
└── static/
    ├── css/main.css        # Full design system
    └── js/main.js          # UI interactivity
```

---

## Getting Started (VS Code)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/mzansibuilds.git
cd mzansibuilds
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Copy `.env.example` to `.env` (or edit `.env` directly):
```bash
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=1
```

### 5. Run the app
```bash
python run.py
```

Open your browser at **http://localhost:5000**

---

## Demo Accounts

The app seeds demo data on first run:

| Username | Password | Character |
|---|---|---|
| `sipho_dev` | `password` | Full-stack, fintech |
| `amahle_codes` | `password` | ML / NLP engineer |
| `kagiso_builds` | `password` | Mobile dev |

---

## Development Notes

- The SQLite database is created automatically at `instance/mzansibuilds.db` on first run
- Seed data is only inserted if the database is empty
- To reset the database: delete `instance/mzansibuilds.db` and restart the server

---

## GitHub Setup

```bash
git init
git add .
git commit -m "Initial commit — MzansiBuilds platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mzansibuilds.git
git push -u origin main
```

---

## Assessment Competencies Addressed

- **Code Quality** — Blueprint-based Flask architecture, separation of concerns (models/routes/templates)
- **Best Practices** — App factory pattern, environment variables, `.gitignore`, password hashing
- **Code Version Control** — Git-ready structure with meaningful commit history
- **User Centricity** — Full user journey: register → create project → collaborate → ship → celebrate
- **Efficiency** — Single SQLite DB, minimal dependencies, server-side rendering
- **Resourcefulness** — AI-assisted development with own architectural decisions and custom design system

---

*Built with 🌍 for the Derivco Code Skills Challenge*
