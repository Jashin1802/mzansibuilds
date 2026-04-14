# Security Policy

## Overview

Security was treated as a core requirement in MzansiBuilds, not an afterthought.
Every layer of the application was built with security considerations in mind from
the start of development.

---

## Security Measures Implemented

### 1. Password Security
- All passwords are hashed using **PBKDF2-SHA256** via Werkzeug's `generate_password_hash`
- Plaintext passwords are never stored in the database at any point
- Password verification uses `check_password_hash` which is timing-attack resistant

### 2. Authentication & Session Management
- **Flask-Login** manages user sessions securely
- Every protected route is decorated with `@login_required`
- Unauthenticated users are redirected to the login page automatically
- Sessions are signed using a secret key loaded from environment variables

### 3. Authorisation & Ownership Checks
- Every project mutation route (edit, delete, milestone, stage update, complete)
  verifies that `project.user_id == current_user.id` before proceeding
- Unauthorised attempts return **HTTP 403 Forbidden** — they are not silently ignored
- Users cannot raise a hand on their own projects (enforced at route level)

### 4. SQL Injection Prevention
- The application uses **SQLAlchemy ORM** exclusively
- No raw SQL queries are written anywhere in the codebase
- All database interactions go through parameterised ORM methods

### 5. Environment Variable Protection
- The application `SECRET_KEY` is loaded from a `.env` file
- The `.env` file is listed in `.gitignore` and is never committed to version control
- The `instance/` folder containing the SQLite database is also excluded from Git

### 6. CSRF Protection
- `Flask-WTF` is included in the project dependencies to support CSRF token
  generation on all forms

### 7. Input Handling
- Empty form submissions are rejected at the route level before hitting the database
- Stage values are validated against a fixed list (`VALID_STAGES`) before being saved

---

## Known Limitations (Development Build)

| Limitation | Notes |
|---|---|
| SQLite database | Suitable for development. Production should use PostgreSQL |
| No HTTPS enforcement | Should be enforced at the server/proxy level in production |
| No rate limiting | Login route does not currently throttle repeated attempts |
| No email verification | User registration does not verify email addresses |

---

## Reporting a Vulnerability

This is a development/assessment project. If you identify a security issue,
please raise it via a GitHub Issue on this repository.
