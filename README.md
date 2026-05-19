# CivicBridge 🏛️

A Django-based civic complaint management web application that bridges the gap between citizens and government officers. CivicBridge enables residents to file, track, and escalate public grievances while providing officers with a structured dashboard to review, update, and resolve complaints transparently.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Server](#running-the-server)
- [User Roles](#user-roles)
- [Complaint Lifecycle](#complaint-lifecycle)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

CivicBridge is a web platform designed to simplify and digitise the process of civic complaint registration and resolution. Citizens can submit complaints with supporting images, monitor their status in real time, and escalate unresolved issues. Officers are provided with tools to approve, update, and resolve complaints through a dedicated dashboard — with built-in safeguards to prevent invalid state transitions (e.g., escalating an already-resolved complaint).

---

## Features

### For Citizens
- Register and log in securely
- Submit complaints with image attachments
- Edit pending (unprocessed) complaints
- Track complaint status in real time
- Escalate unresolved complaints to higher authorities
- Escalation is automatically blocked for **Resolved** or already **Escalated** complaints

### For Officers
- Dedicated officer dashboard
- View all assigned complaints with status indicators
- Update complaint status (Pending → In Progress → Resolved)
- Escalation option hidden for Resolved or Escalated complaints
- Approve or reject new officer registrations via an admin approval page

### General
- Role-based access control (Citizen / Officer / Admin)
- Complaint image uploads stored under `media/complaint_images/`
- SQLite database for development (easily swappable)
- Clean, responsive HTML/CSS/JS frontend with Django templates

---

## Tech Stack

| Layer        | Technology              |
|--------------|-------------------------|
| Backend      | Python 3, Django        |
| Database     | SQLite3 (default)       |
| Frontend     | HTML5, CSS3, JavaScript |
| Templating   | Django Templates        |
| File Storage | Django media files      |

**Language breakdown:** Python 97.2% · HTML 1.5% · JavaScript 0.7% · CSS 0.5%

---

## Project Structure

```
CivicBridge/
├── bcivic/                  # Django project settings & URL config
│   └── settings.py
├── home/                    # Core app — models, views, URLs
│   ├── models.py            # Complaint, User, Officer models
│   ├── views.py             # All view logic (submit, escalate, update, etc.)
│   └── urls.py
├── NEW-ONE/                 # Secondary app / feature module
├── template/                # Django HTML templates
│   ├── officer_complaint_detail.html
│   └── ...
├── complaint_images/        # Uploaded complaint images (dev)
├── media/
│   └── complaint_images/    # Django MEDIA_ROOT for file uploads
├── db.sqlite3               # SQLite development database
├── manage.py                # Django management CLI
└── TODO.md                  # Development task tracker
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AthiraAnil1612/CivicBridge.git
   cd CivicBridge
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   > If a `requirements.txt` is not present, install Django manually:
   > ```bash
   > pip install django
   > ```

4. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## User Roles

| Role    | Capabilities                                                                 |
|---------|------------------------------------------------------------------------------|
| Citizen | Register, submit complaints, upload images, track status, escalate issues    |
| Officer | View assigned complaints, update status, manage escalations                  |
| Admin   | Approve/reject officer registrations, full access via Django admin panel     |

---

## Complaint Lifecycle

```
Submitted (Pending)
       │
       ▼
   In Progress   ◄──── Officer updates status
       │
       ▼
   Resolved  ──────────── No further escalation allowed
       │
  (or escalate)
       │
       ▼
   Escalated ──────────── No further escalation allowed
```

- Officers **cannot** escalate or change status of a **Resolved** complaint.
- The **Escalate** button is hidden in the officer dashboard for Resolved or Escalated complaints.
- Citizens **cannot** escalate a Resolved or already Escalated complaint.
- Citizens **can edit** a complaint only while it is still **Pending**.

---

## Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please make sure your code follows Django best practices and that all views are tested before submitting.

---

## License

This project is open source. Feel free to use, modify, and distribute it for educational and civic purposes.

---

> Built with ❤️ to empower citizens and streamline civic governance.
