# Profile_MS Microservice

`Profile_MS` is a **Django REST Framework microservice** dedicated to managing user profile, address, and card information. It communicates with `AUTH_MS` for user authentication and token validation. This service is built to be modular, lightweight, and ready for microservice architecture.

---

## Table of Contents

1. [Features](#features)  
2. [Architecture](#architecture)  
3. [Technology Stack](#technology-stack)  
4. [Installation & Setup](#installation--setup)  
5. [Environment Variables](#environment-variables)  
6. [API Endpoints](#api-endpoints)  
7. [Authentication](#authentication)  
8. [Data Models](#data-models)  
9. [Testing](#testing)  
10. [Deployment](#deployment)  

---

## Features

- Fetch and update **user profiles** (first name, last name, alternate email, phone numbers, gender, date of birth)  
- Manage **multiple addresses** per user (home, work, friend, other)  
- Manage **up to 4 cards** per user (credit and debit)  
- Validate **phone numbers** (10 digits)  
- Country code selection for phone numbers  
- Address fields with country, state, city selection  
- Integration with **AUTH_MS** for token verification  
- Fully **RESTful API** design  

---

## Architecture

```
Client (React/Vue/Flutter)
      |
      v
Profile_MS (Django REST Framework)
      |
      v
AUTH_MS (Authentication microservice)
```

- **Profile_MS** never stores passwords or authentication data.  
- It **verifies tokens** via `AUTH_MS` for secure access.  
- Each user’s profile, addresses, and cards are managed locally in `Profile_MS`.

---

## Technology Stack

- **Backend:** Django 6.0, Django REST Framework  
- **Database:** SQLite (for development)  
- **Authentication:** JWT via AUTH_MS  
- **CORS:** Configured to allow frontend apps  
- **Python:** 3.11+  

---

## Installation & Setup

1. **Clone the repository**

```bash
git clone <your_repo_url>
cd profile_ms
```

2. **Create a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Setup environment variables**

Create a `.env` file in the root directory:

```env
DEBUG=True
SECRET_KEY=django-insecure-onfi46j604fe73ny*0q((lku#-m@u)uu0$1&a@i968xs3pe7p3
ALLOWED_HOSTS=127.0.0.1,localhost
AUTH_MS_BASE_URL=http://127.0.0.1:8000/api/auth
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://localhost:3000
```

5. **Run migrations**

```bash
python manage.py migrate
```

6. **Start the development server**

```bash
python manage.py runserver 8001
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enable/disable debug mode |
| `ALLOWED_HOSTS` | Allowed hosts for Django |
| `AUTH_MS_BASE_URL` | Base URL of the authentication microservice |
| `CORS_ALLOWED_ORIGINS` | Frontend origins allowed for cross-origin requests |
| `CSRF_TRUSTED_ORIGINS` | Frontend origins allowed for CSRF protection |

---

## API Endpoints

### Health & Test

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profiles/health/` | GET | Health check of Profile_MS |
| `/profiles/test-auth/` | GET | Test connection with AUTH_MS using token |

### User Profile

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profiles/profile/` | GET | Fetch authenticated user profile |
| `/profiles/profile/` | PUT | Update profile fields (except email/person_id) |

### Address

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profiles/addresses/` | GET | List all addresses for user |
| `/profiles/addresses/` | POST | Create new address |
| `/profiles/addresses/<id>/` | GET | Get address by ID |
| `/profiles/addresses/<id>/` | PUT | Update address by ID |
| `/profiles/addresses/<id>/` | DELETE | Delete address by ID |

### Card

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profiles/cards/` | GET | List all cards for user |
| `/profiles/cards/` | POST | Add new card (max 4 per user) |
| `/profiles/cards/<id>/` | GET | Get card by ID |
| `/profiles/cards/<id>/` | PUT | Update card by ID |
| `/profiles/cards/<id>/` | DELETE | Delete card by ID |

---

## Authentication

- **All endpoints require JWT Bearer token** obtained from AUTH_MS.  
- Token is sent in headers:

```http
Authorization: Bearer <access_token>
```

- Profile_MS verifies token with AUTH_MS before processing requests.

---

## Data Models

### UserProfile

- `person_id` (from AUTH_MS)  
- `email` (from AUTH_MS)  
- `alternate_email`  
- `primary_phone`, `alternate_phone`  
- `primary_country_code`, `alternate_country_code`  
- `first_name`, `last_name`, `gender`, `date_of_birth`

### Address

- `user` (FK)  
- `address_type` (home/work/friend/other)  
- `line1`, `line2`  
- `country`, `state`, `city`  
- `zip_code`  
- `phone_number`  
- `is_default`  

### Card

- `user` (FK)  
- `card_type` (credit/debit)  
- `card_brand`  
- `card_number`  
- `card_holder_name`  
- `expiry_month`, `expiry_year`  
- `is_default`  
- Maximum **4 cards per user**  

---

## Testing

- Use **Postman** or **Insomnia** to test API endpoints  
- Include **Authorization header** with Bearer token  
- Test **CRUD operations** for profile, addresses, and cards

---

## Deployment

- Can be deployed as **Docker container** or on **Render / AWS / Heroku**  
- Ensure **SECRET_KEY** and **AUTH_MS_BASE_URL** are properly set in production environment  
- Use production-ready WSGI/ASGI server (e.g., Gunicorn, Daphne)  

---

## Notes

- **Profile_MS is stateless** regarding authentication  
- All authentication is delegated to AUTH_MS  
- Designed to support **microservice architecture** with independent scaling

