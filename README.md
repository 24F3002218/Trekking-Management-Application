# Trek Management Application

A full-stack Flask web application for managing trekking operations with three roles: **Admin**, **Trek Staff**, and **Trekker (User)**.

## Tech Stack

- **Backend:** Flask, Flask-Login, Flask-SQLAlchemy, Flask-WTF
- **Frontend:** Jinja2, HTML, Bootstrap 5, minimal JavaScript
- **Database:** SQLite (created automatically via SQLAlchemy)
- **Auth:** Flask-Login sessions, Werkzeug password hashing

## Setup & Run

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
cd D:\MAD-1
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
```

Alternatively:

```bash
set FLASK_APP=app.py
flask run
```

Open **http://localhost:5000** in your browser.

The SQLite database (`trekking.db`) is created automatically on first run. Sample treks, staff, and users are seeded for demo purposes.

## Default Credentials

| Role  | Email              | Password  |
|-------|--------------------|-----------|
| Admin | admin@trek.com     | admin123  |

### Sample Demo Accounts (seeded)

| Role   | Email            | Password |
|--------|------------------|----------|
| Staff  | rajesh@trek.com  | staff123 |
| Staff  | priya@trek.com   | staff123 |
| User   | ananya@trek.com  | user123  |
| User   | vikram@trek.com  | user123  |

> **Note:** Admin account is pre-seeded. There is no admin registration. Staff must register and await admin approval.

## Project Structure

```
D:\MAD-1\
├── app.py                 # Application factory & entry point
├── config.py              # Configuration
├── forms.py               # WTForms definitions
├── requirements.txt
├── api.yaml               # OpenAPI spec for JSON endpoints
├── models/
│   ├── user.py            # User model (admin/staff/user roles)
│   ├── staff_profile.py   # Staff approval status
│   ├── trek.py            # Trek model
│   └── booking.py         # Booking model
├── routes/
│   ├── auth.py            # Login, register, logout
│   ├── admin.py           # Admin CRUD & management
│   ├── staff.py           # Staff trek management
│   ├── user.py            # Trekker booking & profile
│   └── api.py             # JSON API endpoints
├── templates/             # Jinja2 HTML templates
├── static/css/style.css   # Custom styles
└── utils/
    ├── decorators.py      # Role-based access control
    └── seed.py            # Admin & sample data seeding
```

## Features

### Admin
- Dashboard with stats (treks, users, staff, bookings) + Chart.js doughnut chart
- CRUD treks (add/edit/delete)
- Approve/reject/blacklist staff (Pending / Approved / Blacklisted tabs)
- Assign staff to treks
- View all users, staff, treks, bookings
- Search treks, staff, users by name or ID
- Blacklist/restore users and staff
- View historical trekking data

### Trek Staff
- Self-register (requires admin approval)
- Dashboard with assigned treks and participant counts
- Update trek slots and status (Open/Closed)
- View participant list
- Mark trek as started → completed (only assigned staff)
- Access restricted to assigned treks only

### Trekker (User)
- Self-register and login
- Dashboard with open treks and recent bookings
- Search/filter treks by location and difficulty
- Book open treks (overbooking prevented)
- Cancel active bookings (slots restored)
- View booking status and trekking history
- Edit profile

## Business Rules

- Users can book only **Open** treks with available slots
- Overbooking is prevented (slot decremented on book, restored on cancel)
- Only **assigned staff** can manage a trek
- Complete booking history is maintained (Booked / Cancelled / Completed)
- Blacklisted users cannot login or use the system
- Staff must be **approved** before accessing the staff dashboard

## JSON API Endpoints

All API routes require an active login session:

| Method | Endpoint            | Description                    |
|--------|---------------------|--------------------------------|
| GET    | `/api/treks`        | List treks (optional `?status=`) |
| GET    | `/api/treks/<id>`   | Trek details                   |
| GET    | `/api/bookings`     | Bookings (scoped by role)      |
| GET    | `/api/stats`        | Admin statistics               |

See `api.yaml` for OpenAPI documentation.

## Environment Variables (optional)

| Variable         | Default           |
|------------------|-------------------|
| SECRET_KEY       | (dev default)     |
| DATABASE_URL     | sqlite:///trekking.db |
| ADMIN_EMAIL      | admin@trek.com    |
| ADMIN_PASSWORD   | admin123          |
