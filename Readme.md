# Noor Stitching Institute - Backend API

A robust, production-ready Django REST Framework backend for managing the Noor Stitching Institute. This system handles the entire lifecycle of the institute, including student admission, course management, financial tracking, attendance, and certificate issuance with QR code verification.

## 🚀 Key Features

* **🔐 Authentication & Roles**
  * Secure JWT Authentication (`simplejwt`).
  * Role-Based Access Control (RBAC): Administrators (Staff) vs. Students.
  * Profile management and password reset flows via Email (SendGrid).

* **👤 Student Management**
  * Detailed student profiles with guardian info.
  * **Measurements Tracking:** Dedicated module to record body measurements (Neck, Chest, Waist, etc.) for stitching courses.
  * Self-service portal for students to view their own data.

* **📚 Courses & Materials**
  * Course creation with duration, fees, and syllabus.
  * **Digital Library:** Upload course materials (PDFs, Images) or external links.
  * Student Enrollment tracking (Active/Dropped/Completed).

* **📅 Attendance System**
  * Daily attendance marking (Present, Absent, Late, Excused).
  * Analytics dashboard for attendance rates.
  * **Auto-Completion Logic:** Automatically marks courses as "Completed" when attendance thresholds are met.

* **💰 Finance & Accounting**
  * **Fee Receipts:** Generate professional PDF receipts automatically using `WeasyPrint`.
  * **Expense Tracking:** Categorized expenses (Rent, Salary, Materials, etc.).
  * **Dashboard:** Financial analytics (Revenue vs. Expenses) and charts.
  * **Outstanding Fees:** Reports to identify students with pending payments.

* **🏆 Certification**
  * Generate PDF Certificates upon course completion.
  * **QR Code Verification:** Publicly accessible endpoint to verify certificate authenticity via QR scan.
  * Revocation system for invalidating certificates.

* **📢 Events & Notifications**
  * Internal notification system for alerts.
  * Institute-wide event calendar.

---

## 🛠️ Tech Stack

* **Framework:** Python 3.11+, Django 5.2, Django REST Framework 3.16.
* **Database:** SQLite (Dev), PostgreSQL (Production - via `dj_database_url`).
* **Authentication:** JWT (JSON Web Tokens).
* **PDF Engine:** [WeasyPrint](https://weasyprint.org/).
* **Email Service:** SendGrid.
* **Documentation:** OpenAPI 3.0 (Swagger & Redoc via `drf-spectacular`).
* **Server:** Gunicorn, Whitenoise (Static files).
* **Containerization:** Docker.

---

## ⚙️ Local Setup & Installation

### Prerequisites
* Python 3.11+
* **System Dependencies (Important for WeasyPrint):**
  You must install libraries required for PDF generation (Pango, Cairo, GDK-Pixbuf).
  * *Windows:* [Follow WeasyPrint Guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows) (usually involves installing GTK3).
  * *Linux:* `sudo apt-get install build-essential libpq-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`
  * *macOS:* `brew install pango libffi cairo gdk-pixbuf`

### Steps

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/navafv/noor-backend.git](https://github.com/navafv/noor-backend.git)
    cd noor-backend
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**
    Create a `.env` file in the root directory. Use `.env.example` as a reference.
    ```bash
    cp .env.example .env
    ```
    *Update `DJANGO_SECRET_KEY` and `SENDGRID_API_KEY` in the `.env` file*.

5.  **Run Migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Create Admin User**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run Server**
    ```bash
    python manage.py runserver
    ```
    Access API at `http://127.0.0.1:8000/api/v1/`

---

## 🐳 Docker Setup

A `Dockerfile` is included for containerized deployment.

1.  **Build the Image**
    ```bash
    docker build -t noor-backend .
    ```

2.  **Run the Container**
    ```bash
    docker run -p 8000:8000 --env-file .env noor-backend
    ```

---

## 📖 API Documentation

The project uses `drf-spectacular` to generate automatic documentation. Once the server is running:

* **Swagger UI:** `http://127.0.0.1:8000/api/docs/swagger/`
* **Redoc:** `http://127.0.0.1:8000/api/docs/redoc/`
* **Schema (YAML):** `http://127.0.0.1:8000/api/schema/`

---

## 🧪 Testing

The project is configured to use `pytest`.

```bash
# Run all tests
pytest

# Run specific app tests
pytest students/tests.py