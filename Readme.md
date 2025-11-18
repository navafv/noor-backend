# Noor Stitching Institute - Backend

This is the complete Django backend for the Noor Stitching Institute management system. It provides a robust, scalable API to manage all aspects of the institute.

## Features

* **👤 Accounts & Roles**: Custom User model with Role-based permissions (Admin, Staff, Student).
* **🎓 Students & Enquiries**: Manages the full student lifecycle from initial enquiry to active student profile.
* **📚 Courses & Batches**: Handles course curriculum, student enrollments, and material distribution.
* **📅 Attendance**: Tracks daily student attendance with auto-completion logic.
* **💵 Finance**: Complete financial tracking, including Fee Receipts (with PDF generation), Expense Tracking, and Outstanding Fee Reports.
* **🪪 Certificates**: Issues and revokes student certificates with automatic PDF generation and QR-code verification.
* **🔔 Notifications**: Internal notification system for students and staff.
* **🎉 Events**: A simple broadcast system for institute-wide events.
* **🔐 Authentication**: Secure JWT (JSON Web Token) authentication.
* **📄 API Documentation**: Automatic OpenAPI (Swagger/Redoc) schema generation.

## Tech Stack

* **Backend**: Django, Django REST Framework
* **Database**: PostgreSQL (Production), SQLite3 (Development)
* **Authentication**: djangorestframework-simplejwt (JWT)
* **PDF Generation**: xhtml2pdf
* **Deployment**: Docker, Gunicorn, Whitenoise

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/navafv/noor-backend.git](https://github.com/navafv/noor-backend.git)
    cd noor-backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Setup environment variables:**
    * Copy `.env.example` to a new file named `.env`.
    * Fill in the required values. `DJANGO_SECRET_KEY` is mandatory.
    * Set `FRONTEND_URL` (e.g., `http://localhost:5173`) for correct link generation in emails/PDFs.
    ```bash
    cp .env.example .env
    ```

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the server:**
    ```bash
    python manage.py runserver
    ```

The API will be available at `http://127.0.0.1:8000/`.  
API documentation is available at `http://127.0.0.1:8000/api/docs/`.