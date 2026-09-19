# Event Registration System

A full-stack Event Management & Registration Platform built with **Django 5.x**, **Django REST Framework**, and a modern **Glassmorphism Single Page Web Interface**.

---

## 🌟 Key Features

- **🎨 Glassmorphism Web Dashboard** — Beautiful, responsive UI available at `http://127.0.0.1:8000/` featuring real-time event browsing, search, category filters, animated capacity progress bars, and modal forms.
- **📅 Events Management** — Create, list, search, and view detailed event information (title, description, venue, start/end time, capacity, organizer).
- **🎫 Real-time Registration System** — Authenticated users can register for events with instant feedback. Handles capacity enforcement, full/past event checks, and cancellation tracking.
- **🔐 Authentication & User Accounts** — User sign-up (`/api/auth/register/`), Token Authentication (`/api/auth/token/`), and Session Auth for Admin panel.
- **🛡️ Concurrency & Lock Management** — Utilizes database row locking (`select_for_update`) within atomic transactions to prevent race conditions during peak registration demand.
- **⚙️ Admin Panel** — Custom Django Admin interface with inline registration tracking and capacity badges.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Django 5.2, Django REST Framework 3.15
- **Frontend:** HTML5, Modern Vanilla CSS3 (Glassmorphism design system), Lucide Icons
- **Database:** SQLite / PostgreSQL (via `psycopg2-binary`)
- **Type Checking & IDE Tools:** Pyrefly, Pyright / VS Code configuration

---

## 📁 Project Structure

```
event_registration_system/
├── manage.py
├── requirements.txt
├── .env.example
├── pyrefly.toml            # Pyrefly static type checker config
├── .vscode/
│   └── settings.json       # VS Code workspace interpreter settings
├── config/                 # Project settings & URL routing
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/
│   └── index.html          # Modern Glassmorphism Web UI
└── events/                 # Django App
    ├── models.py           # Event & Registration models
    ├── serializers.py      # DRF serializers (includes confirmed_count & is_past)
    ├── views.py            # API ViewSets & Registration logic
    ├── urls.py
    ├── permissions.py
    ├── admin.py
    ├── tests.py
    └── migrations/
```

---

## 🚀 Getting Started

### 1. Activate Environment & Install Dependencies

```bash
# Windows
.\venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Migration & Sample Data

```bash
python manage.py migrate
python manage.py test
```

### 3. Default Login Credentials

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Superuser / Admin** | `admin` | `admin123` | Django Admin Portal |
| **Sample User** | `john_doe` | `user123` | Frontend User Testing |

### 4. Run Development Server

```bash
python manage.py runserver
```

Open your browser to **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** to access the interactive web interface!

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| **POST** | `/api/auth/register/` | Register a new user account | None |
| **POST** | `/api/auth/token/` | Obtain DRF Auth Token | None |
| **GET** | `/api/events/` | List events (supports `?upcoming=true`, `?search=`) | None |
| **GET** | `/api/events/{id}/` | Event detail | None |
| **POST** | `/api/events/` | Create a new event | Organizer / Staff |
| **PATCH/DELETE** | `/api/events/{id}/` | Update or delete an event | Organizer / Staff |
| **POST** | `/api/events/{id}/register/` | Register current user for event | Required |
| **GET** | `/api/registrations/` | List user's active & past registrations | Required |
| **DELETE** | `/api/registrations/{id}/` | Cancel a registration | Required (Owner) |
| **PATCH** | `/api/registrations/{id}/cancel/` | Explicit cancel endpoint | Required (Owner) |

---

## 🔬 Running Tests & Code Quality

Run automated unit tests:

```bash
python manage.py test
```

Run static type checking with Pyrefly:

```bash
pyrefly check
```






<img width="1510" height="818" alt="Screenshot 2026-09-19 154214" src="https://github.com/user-attachments/assets/ff9609ba-695a-458b-9c97-909198ae12b6" />

