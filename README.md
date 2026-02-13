# 📍 University Lost & Found System (Team 10)

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.14-a30f2d?style=for-the-badge&logo=django&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Leaflet](https://img.shields.io/badge/Map-Leaflet.js-199900?style=for-the-badge&logo=leaflet&logoColor=white)

A comprehensive location-based platform designed to streamline the process of reporting and recovering lost items within the university campus. This system replaces traditional, disorganized messaging groups with an interactive map-based solution.

---

## 🚀 Tech Stack

### Backend
- **Framework:** Django 4.2 & Django REST Framework (DRF)
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **Authentication:** JWT (JSON Web Token) with Email OTP verification
- **API Documentation:** Swagger UI & ReDoc

### Frontend
- **Core:** Semantic HTML5, CSS3, Vanilla JavaScript (ES6+)
- **Map Interface:** Leaflet.js with OpenStreetMap
- **Architecture:** Client-side rendering consuming RESTful APIs

---

## ✨ Key Features

- **🔐 Secure Authentication:**
  - Email-based One-Time Password (OTP) registration.
  - JWT-based login/logout for secure sessions.
  - User profile management.

- **🗺️ Interactive Map:**
  - Visual pins for **Lost** (Red) and **Found** (Green) items.
  - Precise location selection via click/drag.

- **📦 Item Management:**
  - Upload images, titles, descriptions, and tags.
  - Filter items by status, date, or tags.
  - CRUD operations for item owners.

- **💬 Community Interaction:**
  - **Threaded Comments:** Users can discuss items and reply to specific comments.
  - **Reporting System:** Community moderation where items/comments are auto-flagged after 5 reports.

---

## 🛠️ Installation & Setup

### 1️⃣ Backend Setup (Django)

1. **Clone the repository and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Migration & Seeding:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_tags
   python manage.py createsuperuser
   ```

5. **Environment Configuration:**
   Create a `.env` file in the `backend/lost_found_project` directory (alongside `settings.py`) and configure your email settings for OTP:
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

6. **Run the Server:**
   ```bash
   python manage.py runserver
   ```
   *The API will be available at `http://127.0.0.1:8000/`*

### 2️⃣ Frontend Setup

Since the frontend is built with Vanilla JavaScript, no build process (npm/webpack) is required.

1. **Navigate to the frontend folder:**
   ```bash
   cd frontend
   ```

2. **Configuration:**
   Ensure `assets/js/config.js` points to your local backend:
   ```javascript
   const CONFIG = {
       API_BASE_URL: 'http://127.0.0.1:8000',
       // ...
   };
   ```

3. **Running the App:**
   You can simply open `index.html` in your browser.
   
   *Recommended:* For better API handling and to avoid CORS issues locally, use a lightweight server like **Live Server** (VS Code Extension) or Python's built-in http server:
   ```bash
   # Inside frontend folder
   python -m http.server 3000
   ```
   Then visit: `http://localhost:3000`

---

## 📝 API Endpoints Overview

You can view the full interactive documentation at:  
`http://127.0.0.1:8000/swagger/`

| Module | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/auth/send-otp/` | Trigger OTP email |
| | `POST` | `/api/auth/verify-otp/` | Verify code |
| | `POST` | `/api/auth/login/` | Get Access/Refresh tokens |
| **Items** | `GET` | `/api/items/` | List/Filter items |
| | `POST` | `/api/items/` | Create new item |
| | `GET` | `/api/items/{id}/` | Get item details |
| **Interactions** | `GET` | `/api/items/{id}/comments/` | Get comments for item |
| | `POST` | `/api/comments/add/` | Post a new comment |
| | `POST` | `/api/report/` | Report an item or comment |

---

## 📂 Project Structure

```text
root/
├── backend/
│   ├── interactions/     # Comments & Reports logic
│   ├── items/            # Lost & Found Items logic
│   ├── users/            # Auth & Profile logic
│   ├── manage.py
│   └── requirements.txt
│
└── frontend/
    ├── assets/
    │   ├── css/          # Stylesheets
    │   ├── js/           # Logic (api.js, details.js, maps.js)
    │   └── images/
    ├── index.html        # Main Map View
    ├── item-det # Single Item View
    └── login.html        # Auth Pages

---

<p align="center">
  <b>Developed by Team 10</b><br>
  University Lost & Found Project
</p>
ect
</p>
