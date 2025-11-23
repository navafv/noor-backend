# Noor Stitching Institute - Management System Backend

A comprehensive, production-ready REST API built with **Django 5.2** and **Django REST Framework** to manage the entire lifecycle of a stitching and fashion design institute. This system handles student admissions, body measurements, course progression, financial accounting, attendance tracking, and digital certification.

---

## 🚀 Key Features

### 🔐 Authentication & Roles
* **JWT Authentication:** Secure, stateless authentication using `simplejwt`.
* **RBAC (Role-Based Access Control):** Distinct permissions for **Admins/Staff** (Full access) vs **Students** (Read-only access to own data).
* **Password Management:** Secure reset flows via Email (SendGrid integration).

### 👤 Student & Course Management
* **Digital Profiles:** Manage student details, guardian info, and addresses.
* **Measurements Tracking:** Dedicated module to record specific body measurements (Neck, Chest, Waist, Inseam, etc.) for tailoring courses.
* **Course Materials:** Admins can upload PDFs/Images or link external resources; students can download materials for their enrolled courses.
* **Enrollment Lifecycle:** Track status (`Active`, `Completed`, `Dropped`) and dates.

### 📅 Smart Attendance
* **Daily Tracking:** Mark attendance (Present, Absent, Late, Excused).
* **Auto-Completion:** Automatically marks a student's enrollment as **"Completed"** once they meet the required attendance threshold (e.g., 36 days).
* **Analytics:** Dashboard providing attendance rates and daily trends.

### 💰 Finance & Accounting
* **Fee Receipts:** Auto-generate professional **PDF Receipts** using `WeasyPrint`.
* **Expense Tracking:** Categorize institute expenses (Rent, Salary, Materials).
* **Financial Dashboard:** Real-time analytics of Revenue vs. Expenses.
* **Outstanding Fees:** Logic to identify and list students with pending payments.

### 🏆 Certification & Verification
* **PDF Certificates:** Auto-generate completion certificates.
* **QR Code Verification:** Public endpoint to verify certificate authenticity via UUID hash.
* **Revocation:** Admins can revoke certificates if necessary.

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
    * *Linux (Debian/Ubuntu):*
        ```bash
        sudo apt-get install build-essential libpq-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
        ```
    * *macOS:* `brew install pango libffi cairo gdk-pixbuf`

### 2. Clone & Install
```bash
# Clone the repo
git clone [https://github.com/navafv/noor-backend.git](https://github.com/navafv/noor-backend.git)
cd noor-backend

# Create Virtual Environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Mac/Linux)
source .venv/bin/activate

# Install Python Dependencies
pip install -r requirements.txt