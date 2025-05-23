# TravelSwap

TravelSwap is a Django-based holiday house exchange platform that allows users to browse, like, and match with other vacation homes based on preferences. It features a Tinder-style UI, booking calendar, in-app messaging, and more.

## Table of Contents

- [User Stories](#user-stories)
- [Features](#features)
- [Screenshots](#screenshots)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Credits](#credits)
- [Future Features](#future-features)

---

## User Stories

### Visitor

#### Visitors (Non-Registered)

As a non-registered visitor, I can view the Home and About pages,
so that I can understand what the platform offers before signing up.

- If as a non-registered visitor, I try to access the travel log page, I will be prompted to login/register.

- If as a non-registered visitor, I try to like a profile, I will be prompted to login/register.

#### User Registration & Authentication

As a visitor, I can register/log in/out, so that I can access features securely.

- Visitor can register with email and password.

- Login and logout buttons work correctly.

- Password reset functionality exists.

### Registered User

### Admin

## Features

- Tinder-style profile swipe interface
- Contact form with email integration (logged to terminal for assessment)
- Dynamic calendar-based booking proposal system
- In-app notifications for real-time engagement
- Profile image gallery with modal preview and file validations
- Filterable home criteria (pets, pool, beach, rural, etc.)
- Travel log to view matched/liked homes

---

## Screenshots

## Technologies Used

- **Python 3.12**, **Django 4.2**
- PostgreSQL
- Bootstrap 5
- JavaScript (modals, alerts)
- Cloudinary (for image hosting)
- GitHub Pages / Heroku (for deployment)

## Installation Instructions

To run locally:

git clone https://github.com/IeuanPriede/travel-swap.git
cd travel-swap
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CLOUDINARY_URL=your_cloudinary_url

## Testing

Please refer to the TESTING.md file for all testing performed.

## Deployment

## Future Features / Known Issues

## Credits