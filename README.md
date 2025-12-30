# 📍 University Lost & Found System (Team 10)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.14-red)
![React](https://img.shields.io/badge/React-18.x-61DAFB)
![Leaflet](https://img.shields.io/badge/Map-Leaflet.js-orange)

A location-based platform designed to replace telegram groups for lost and found items within the university campus. Users can pin items on the map, comment, and report issues.

---

## 🚀 Tech Stack

- **Backend:** Python, Django, Django REST Framework (DRF)
- **Database:** SQLite (Default for development)
- **Frontend:** React.js
- **Map Provider:** Leaflet.js / OpenStreetMap
- **Authentication:** JWT (JSON Web Token) with OTP support

---

## ✨ Features

- **User Authentication:** Sign up with Email/OTP, Login (JWT), and Profile management.
- **Map Integration:** View lost/found items visually on the university map.
- **Item Management:** Post items with images, tags, and location.
- **Interactions:** Threaded comments system under items.
- **Moderation:** Community-based reporting system (auto-hide content after 5 reports).

---

## 🛠️ How to Run

### 1️⃣ Backend Setup (Django)

1.  **Navigate to the backend folder:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Setup Database & Seed Data:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py seed_tags      # Adds default tags (Keys, Wallet, etc.)
    python manage.py createsuperuser # Create an admin account (Optional)
    ```

5.  **Run the Server:**
    ```bash
    python manage.py runserver
    ```

6.  **Access API Documentation:**
    - Swagger UI: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
    - ReDoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

### 2️⃣ Frontend Setup (React)

1.  **Navigate to the frontend folder:**
    ```bash
    cd frontend
    ```

2.  **Install Node modules:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm start
    ```
    - The application should open at [http://localhost:3000](http://localhost:3000).

---

## 📝 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/send-otp/` | Send OTP to email |
| `POST` | `/api/auth/login/` | Get JWT Tokens |
| `GET` | `/api/items/` | List all items |
| `POST` | `/api/items/` | Create a new item (Auth required) |
| `GET` | `/api/map-data/` | Lightweight map data (Lat/Lon) |
| `POST` | `/api/comments/add/` | Add a comment |

---

**Developed by Team 10**
