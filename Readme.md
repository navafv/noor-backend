# Noor Stitching Institute - Management System Backend

A lightweight, specialized REST API built with **Django 5.2** and **Django REST Framework** to manage the daily operations of Noor Stitching Institute. This system focuses on student enrollment, attendance, financial tracking, and certification.

---

## 🚀 Key Features

### 🔐 Authentication & Roles
* **JWT Authentication:** Secure, stateless authentication using `simplejwt`.
* **RBAC (Role-Based Access Control):** Distinct permissions for **Admins/Staff** (Full access) vs **Students** (Read-only access to own data).
* **Password Management:** Secure reset flows via Email (SendGrid integration).

### 👤 Student & Course Management
* **Digital Profiles:** Manage student details, guardian info, and addresses.
* **Course Enrollment:** Track enrollment status (`Active`, `Completed`, `Dropped`) and dates.
* **Active Student Tracking:** Easily filter and manage students currently studying.

### 📅 Attendance System
* **Daily Tracking:** Mark attendance for enrolled students (Present, Absent, Late, Excused).
* **Auto-Completion Logic:** Automatically marks a student as "Completed" when they meet the required attendance threshold (e.g., 36 days).
* **History & Analytics:** Students can view their own attendance history; Admins see institute-wide stats.

### 💰 Finance & Accounting
* **Fee Receipts:** Auto-generate professional **PDF Receipts** using `WeasyPrint`.
* **Expense Tracking:** Record and categorize institute expenses (Rent, Salary, Materials, etc.).
* **Outstanding Fees:** One-click view to identify students with pending fee balances.
* **Financial Dashboard:** Real-time summary of Income vs. Expenses.

### 🏆 Certification & Verification
* **PDF Certificates:** Auto-generate completion certificates for eligible students.
* **QR Code Verification:** Public endpoint to verify certificate authenticity via UUID hash.
* **Revocation:** Admins can revoke certificates if necessary.

### 🔔 Notifications
* **Broadcast System:** Admins can send push notifications to all currently active students.
* **In-App Inbox:** Students receive updates directly in their app.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.11+, Django 5.2, Django REST Framework 3.16
* **Database:** SQLite (Dev), PostgreSQL (Production via `dj_database_url`)
* **Authentication:** JWT (JSON Web Tokens)
* **PDF Generation:** [WeasyPrint](https://weasyprint.org/)
* **Documentation:** OpenAPI 3.0 (Swagger/Redoc via `drf-spectacular`)
* **Server:** Gunicorn + Whitenoise (Static files)
* **Containerization:** Docker
* **Testing:** Pytest

---

## ⚙️ Local Development Setup

### 1. Prerequisites
* Python 3.11 or higher
* **WeasyPrint Dependencies:** You must install system libraries for PDF generation.
    * *Windows:* [Install GTK3 installer](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer).
    * *Linux (Debian/Ubuntu):* `sudo apt-get install build-essential libpq-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`
    * *macOS:* `brew install pango libffi cairo gdk-pixbuf`

### 2. Clone & Install
```bash
# Clone the repo
git clone <repository-url>
cd noor-backend

# Create Virtual Environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Mac/Linux)
source .venv/bin/activate

# Install Python Dependencies
pip install -r requirements.txt