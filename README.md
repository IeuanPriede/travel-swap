# TravelSwap

![TravelSwap Banner](static\images\documentation\travelswap-banner.png)

**TravelSwap** is a Django-based holiday house exchange platform. Users can register, create profiles showcasing their homes, like and match with other users, and arrange house swaps through an interactive, Tinder-style interface. The platform includes dynamic filtering, messaging, booking calendar requests, notifications, and photo uploads.

---

## Table of Contents

- [Features](#features)
- [User Stories](#user-stories)
- [Screenshots](#screenshots)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Credits](#credits)
- [Future Features](#future-features)

---

## Features

### 🏠 Profile Features
- User registration and authentication
- Profile creation and editing
- Multiple image uploads for homes (carousel/gallery)
- Country dropdown and home descriptions
- Feature checkboxes (pets, pool, beach, rural, etc.)

### 👍 Matchmaking & Search
- Tinder-style profile swiping (like/skip)
- Match confirmation when both users like each other
- Dynamic filters for finding relevant homes based on selected criteria

### 📅 Booking Requests
- Calendar interface for selecting available dates
- Booking request creation, amendment, acceptance, or denial
- Date availability shown based on matched user's calendar

### 📩 Messaging & Notifications
- In-app messaging system between matched users
- Notification system for match alerts, messages, and booking status

### 📓 Travel Log
- Travel log for storing liked/matched homes
- Link to view full profiles of matched users

---

## User Stories

### Visitors
- Can view the home and about pages
- Prompted to sign up when trying to like or access features

### Registered Users
- Can create and update their home profile
- Can like other users and get matched
- Can see suggested profiles based on filters
- Can message matched users
- Can manage booking requests and travel log

---

## Screenshots

### Home Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\Homepage1Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\Homepage2Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage1Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage2Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage3Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage4Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  </tr>
</table>

### About Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\About1Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\About2Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\About2Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage2Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\About3Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\About4Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  </tr>
</table>

### Travel Log Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\Travellog1Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\Travellog2Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Travellog1Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Travellog2Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Travellog3Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  </tr>
</table>

### View Profle Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\ViewProfile1Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\ViewProfile2Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\ViewProfile1Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\ViewProfile2Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\ViewProfile3Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\ViewProfile4Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\ViewProfile5Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  </tr>
</table>

### Profile Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\MyProfile1Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\MyProfile2Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage1Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage2Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage3Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\Homepage4Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  </tr>
</table>

### Edit Profile Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\EditProfile1Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\EditProfile2Laptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\EditProfile1Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\EditProfile2Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\EditProfile3Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\EditProfile4Phone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  </tr>
</table>

### Login Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\LoginPageLaptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\LoginPhone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  </tr>
</table>

### Register Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\RegisterLaptop.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\RegisterPhone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  </tr>
</table>

### 404 Page

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\screenshots\laptop\404Page.png" width="600"><br>
      <sub>Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\screenshots\phone\404PagePhone.png" width="300"><br>
      <sub>Mobile View</sub>
    </td>
  <tr>
</table>

---

## Wireframes

### Laptop

<table>
  <tr>
    <td align="center">
      <img src="static\images\documentation\wireframes\laptop\HomePageLaptop.jpg" width="300"><br>
      <sub>Home Page – Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\wireframes\laptop\AboutUsLaptop.jpg" width="300"><br>
      <sub>About Page – Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\wireframes\laptop\Travellog.jpg" width="300"><br>
      <sub>Travel Log Page – Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\wireframes\laptop\ViewProfileLaptop.jpg" width="300"><br>
      <sub>View Profile Page – Laptop View</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="static\images\documentation\wireframes\laptop\MyProfileLaptop.jpg" width="300"><br>
      <sub>Profile Page – Laptop View</sub>
    </td>
    <td align="center">
      <img src="static\images\documentation\wireframes\laptop\EditProfileLaptop.jpg" width="300"><br>
      <sub>Profile Edit Page – Laptop View</sub>
    </td>
        <td align="center">
      <img src="static\images\documentation\wireframes\laptop\LoginPageLaptop.jpg" width="300"><br>
      <sub>Login Page – Laptop View</sub>
    </td>
        <td align="center">
      <img src="static\images\documentation\wireframes\laptop\RegisterPageLaptop.jpg" width="300"><br>
      <sub>Register Page – Laptop View</sub>
    </td>
        <td align="center">
      <img src="static\images\documentation\wireframes\laptop\404PageLaptop.jpg" width="300"><br>
      <sub>404 Page – Laptop View</sub>
    </td>
  </tr>
</table>

### Mobile

<p align="center">
  <img src="static/images/documentation/wireframes/phone/HomePhone.jpg" width="120" alt="Home Page – Mobile View">
  <img src="static/images/documentation/wireframes/phone/AboutPhone.jpg" width="120" alt="About Page – Mobile View">
  <img src="static/images/documentation/wireframes/phone/TravellogPhone.jpg" width="120" alt="Travel Log Page – Mobile View">
  <img src="static/images/documentation/wireframes/phone/ViewProfilePhone.jpg" width="120" alt="View Profile Page – Mobile View">
  <img src="static/images/documentation/wireframes/phone/MyProfilePhone.jpg" width="120" alt="Profile Page – Mobile View">
  <img src="static/images/documentation/wireframes/phone/EditProfilePhone.jpg" width="120" alt="Profile Edit Page – Mobile View">
  <img src="static/images/documentation/wireframes/phone/LoginPhone.jpg" width="120" alt="Login Page – Mobile View">
  <img src="static/images/documentation/wireframes/phone/CreateAccountPhone.jpg" width="120" alt="Register Page – Mobile View">
  <img src="static/images/documentation/wireframes/phone/404PagePhone.jpg" width="120" alt="404 Page – Mobile View">
</p>
<p align="center">
  <sub>Mobile wireframes</sub>
</p>

---

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python 3, Django
- **Database**: SQLite3 (local), PostgreSQL (production)
- **Media Storage**: Cloudinary
- **Version Control**: Git & GitHub
- **Deployment**: Heroku
- **Others**: AJAX, Django Messages Framework, Django Crispy Forms

---

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/travel-swap.git
    cd travel-swap
    ```

2. Create a virtual environment and install dependencies:
    ```bash
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

3. Create a `.env` file and configure:
    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_URL=your_postgresql_db
    CLOUDINARY_URL=your_cloudinary_url
    ALLOWED_HOSTS=localhost,127.0.0.1
    ```

4. Run migrations and start server:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

## Usage

- Register an account and create your home profile
- Use the home page to browse and like other properties
- Match and chat with other users
- Arrange home swaps using the booking calendar

---

## Testing

See [TESTING.md](./TESTING.md) for full testing strategy and test results.

Basic test commands:
```bash
python manage.py test
```

---

## Deployment

This app is deployed on Heroku.

To deploy your own version:
- Ensure you have a Heroku account
- Use the `Procfile`, `requirements.txt`, and `runtime.txt`
- Connect GitHub repo to Heroku
- Set environment variables in Heroku settings

---

## Credits

- Django documentation
- Bootstrap for styling
- Code Institute for the course scaffold
- Cloudinary for media hosting

---

## Future Features

- Review system for homes and guests
- Enhanced messaging (read receipts, typing indicators)
- Mobile responsiveness improvements
- Email notifications for key events

---

Happy swapping! 🌍
