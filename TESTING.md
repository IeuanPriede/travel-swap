# TravelSwap - Testing

![TravelSwap Banner](static/images/documentation/travelswap-banner.png)

Testing was ongoing throughout the entire build. During development I made use of Googles Developer Tools to ensure everything was working as expected and to assist me with troubleshooting when things didn't work as they should.

I have gone through each page of the site using the Chrome Developer Tools to ensure each page is responsive on a variety of different screen sizes and devices, as well as manually testing this using a variety of devices in person.

## Validation Testing

### HTML

- All templates passed the W3C Markup Validation Service with no critical errors.
- Minor warnings about Bootstrap-related attributes were ignored, as they do not affect rendering or accessibility.

#### - Home page
![Html Validator](static\images\documentation\html-validator.png)

#### - About page
![Html Validator](static\images\documentation\html-validator.png)

#### - Travel Log page
![Html Validator](static\images\documentation\html-validator.png)

#### - View Profile page
![Html Validator](static\images\documentation\html-validator.png)

#### - Profile page
![Html Validator](static\images\documentation\profile-warning.png)

Django code, not recognized in validator.

#### - Edit Profile page
![Html Validator](static\images\documentation\profile-warning.png)

Django code, not recognized in validator.

#### - Register Page

![Html Validator](static\images\documentation\html-validator.png)

#### Login Page

![Html Validator](static\images\documentation\html-validator.png)

### CSS

![CSS Validator](static/images/documentation/css%20validator.png)

### JavaScript

- JavaScript code was linted using JShint with standard settings.
- No major syntax errors or warnings were present.

![JShint Validator](static\images\documentation\jshint.png)

### Python

#### Automated Testing

- Tests were written using `unittest`-based Django `TestCase` classes.
- Tests were run using the Django command:  
  ```bash
  python manage.py test

#### Profiles Models 

| Test Name                        | Description                                        | Expected Result                                    | Pass/Fail |
|----------------------------------|----------------------------------------------------|-----------------------------------------------------|-----------|
| test_profile_str                             | Profile with user and country               | Returns 'username - country'                      | ✅ |
| test_profile_defaults                        | Profile created without optional fields     | is_visible=True and blank fields are allowed      | ✅ |
| test_house_image_str                         | HouseImage linked to profile                | Returns 'Image for username'                      | ✅ |
| test_image_validator_rejects_large_file      | Upload file >2MB                            | Raises ValidationError                            | ✅ |
| test_image_validator_rejects_invalid_type    | Upload file with invalid MIME type          | Raises ValidationError                            | ✅ |
| test_match_response_str                      | MatchResponse for a like/dislike            | Returns 'user liked/disliked user'                | ✅ |
| test_match_response_unique_constraint        | Duplicate like by same user to same profile | Raises IntegrityError due to unique_together rule | ✅ |

#### Profiles Forms

| Test Name                        | Description                                        | Expected Result                                     | Pass/Fail |
|----------------------------------|----------------------------------------------------|-----------------------------------------------------|-----------|
| test_custom_user_creation_valid_data         | Valid username, email, matching passwords    | Form is valid                                      | ✅ |
| test_custom_user_creation_blank_username     | Username is blank or spaces only             | ValidationError: Username cannot be blank         | ✅ |
| test_custom_user_creation_blank_email        | Email is blank or spaces only                | ValidationError: Email cannot be blank            | ✅ |
| test_user_form_blank_username                | UserForm submitted with blank username       | ValidationError: Username cannot be blank         | ✅ |
| test_user_form_blank_email                   | UserForm submitted with blank email          | ValidationError: Email cannot be blank            | ✅ |
| test_profile_form_blank_bio                  | ProfileForm submitted with blank bio         | ValidationError: Bio cannot be blank              | ✅ |
| test_profile_form_blank_house_description    | ProfileForm with blank house description     | ValidationError: House description cannot be blank| ✅ |
| test_image_form_large_file                   | Image >2MB uploaded                          | ValidationError: Image size must be under 2MB     | ✅ |
| test_image_form_invalid_format               | Image not JPEG/PNG                           | ValidationError: Only JPEG and PNG allowed        | ✅ |
| test_contact_form_blank_name                 | ContactForm with blank name                  | ValidationError: Name cannot be blank             | ✅ |
| test_contact_form_blank_email                | ContactForm with blank email                 | ValidationError: Email cannot be blank            | ✅ |
| test_contact_form_blank_subject              | ContactForm with blank subject               | ValidationError: Subject cannot be blank          | ✅ |
| test_contact_form_blank_message              | ContactForm with blank message               | ValidationError: Message cannot be blank          | ✅ |

#### Profiles Views

| Test Name                        | Description                                        | Expected Result                                                                 | Pass/Fail |
|----------------------------------|----------------------------------------------------|---------------------------------------------------------------------------------|-----------|
| test\_profile\_view\_authenticated\_user            | Logged-in user accesses profile page              | 200 OK, template used, context contains profile data           | ✅      |
| test\_profile\_view\_redirects\_if\_not\_logged\_in | Anonymous user tries to view /profiles/           | Redirect to login with `next=/profiles/`                       | ✅      |
| test\_edit\_profile\_redirects\_if\_not\_logged\_in | Anonymous user tries to access edit profile page  | Redirects to login page with `?next=/edit_profile/`            | ✅      |
| test\_edit\_profile\_view\_get\_logged\_in          | Logged-in user accesses edit profile via GET      | Page loads with user form, profile form, formset               | ✅      |
| test\_edit\_profile\_post\_valid\_data              | Logged-in user submits valid profile data         | Profile updated, redirects to `profiles` view                  | ✅      |
| test\_edit\_profile\_post\_invalid\_data            | Logged-in user submits invalid data               | Form re-renders with validation errors                         | ✅      |
| test\_upload\_valid\_image                          | Logged-in user uploads a valid image              | Image saved and user redirected to `edit_profile`              | ✅      |
| test\_upload\_invalid\_image                        | Logged-in user uploads invalid (non-image) file   | Form error shown: “There was a problem updating images.”       | ✅      |
| test\_redirects\_if\_not\_logged\_in (upload)       | Unauthenticated user tries to POST image upload   | Redirects to login page with `?next=/profiles/upload-images/`  | ✅      |
| test\_delete\_with\_correct\_password               | Logged-in user submits correct password to delete | User deleted, redirected to home                               | ✅      |
| test\_delete\_with\_incorrect\_password             | Logged-in user submits wrong password             | Redirects to edit profile, user not deleted                    | ✅      |
| test\_redirects\_if\_not\_logged\_in (delete)       | Unauthenticated user tries to delete profile      | Redirects to login page with `?next=/profiles/delete-profile/` | ✅      |
| test\_register\_view\_get                 | Anonymous user visits the registration page            | 200 OK, form rendered, correct template used            | ✅      |
| test\_register\_view\_post\_valid\_data   | User submits valid registration form                   | User is created and logged in, redirected to `profiles` | ✅      |
| test\_register\_view\_post\_invalid\_data | User submits invalid form (e.g., mismatched passwords) | Form re-renders with appropriate validation errors      | ✅      |
| test\_register\_view\_get                 | Anonymous user visits the registration page            | 200 OK, form rendered, correct template used            | ✅      |
| test\_register\_view\_post\_valid\_data   | User submits valid registration form                   | User is created and logged in, redirected to `profiles` | ✅      |
| test\_register\_view\_post\_invalid\_data | User submits invalid form (e.g., mismatched passwords) | Form re-renders with appropriate validation errors      | ✅      |
| test\_redirects\_if\_not\_logged\_in  | Unauthenticated user tries to delete image      | Redirect to login                             | ✅      |
| test\_forbidden\_if\_not\_owner       | Logged-in user who doesn’t own the image        | 403 Forbidden returned                        | ✅      |
| test\_successful\_deletion\_by\_owner | Correct user sends POST request to delete image | Image deleted, response code 204 (No Content) | ✅      |
| test\_invalid\_method\_returns\_400   | Owner tries to delete image via GET request     | 400 Bad Request, JSON error response returned | ✅      |
| test\_home\_view\_unauthenticated  | Loads home page without login                           | 200 OK, profile context present if any visible profiles exist | ✅      |
| test\_home\_view\_authenticated\_excludes\_own\_and\_responded | Logged-in user sees only unresponded, non-self profiles | Own and previously liked/disliked 
|                                                                |                                                         |   profiles are excluded       | ✅      |
| test\_home\_view\_with\_filters  | Filters by pets\_allowed, pool                          | Profile shown if it matches filter criteria                   | ✅      |
| test\_home\_view\_with\_location\_filter| Filters by location                               | Profile shown if it matches location                          | ✅      |
| test\_home\_view\_with\_valid\_date\_range  | Filters by available\_dates range             | Profile shown if it includes range start or end               | ✅      |
| test\_home\_view\_with\_invalid\_date\_range| Invalid date range query                      | No crash, profile list unaffected                             | ✅      |
| test\_home\_view\_ajax\_returns\_partial| Loads profile card via AJAX                       | Returns JSON with rendered HTML                               | ✅      |
| test_post_without_session_returns_fallback_html   | Made the only profile invisible to trigger "No more profiles"                                        | ✅    |
| test_post_with_valid_session_returns_profile_html | Changed `"profile-card"` check to `"Next Home"` since that string reliably appears in your real HTML | ✅    |
| test_post_with_only_one_profile_shows_alert       | No change — this one already works correctly                                                         | ✅    |
| test_get_method_disallowed                        | No change — your view now handles non-POST methods properly with `HttpResponseNotAllowed`            | ✅    |
| test_like_profile_creates_matchresponse           | New test — verifies MatchResponse creation, proper JSON response, and like success message            | ✅    |
| test_unlike_profile_removes_match_and_redirects   | New test — confirms MatchResponse is deleted, redirects, and shows success message                    | ✅    |
| test_travel_log_mutual_match_flag | Verifies mutual match logic sets `is_mutual=True` when both users liked each other | ✅      |
| test_view_profile_get_authenticated | Tests that a matched user can access another profile and see messaging, booking, and review features | ✅ |
| test_get_latest_booking_returns_most_recent | Confirms correct filtering and ordering of BookingRequest queries                         | ✅ |
| test_handle_booking_request_valid           | Sends a booking request, checks creation and redirect, confirms notification exists   | ✅ |
| test_handle_booking_response_accept         | Simulates recipient accepting a booking, confirms DB update and redirect                   | ✅ |
| test_handle_booking_response_amend          | Simulates recipient amending booking dates, validates update and redirect                  | ✅ |
| test\_handle\_booking\_cancel | Simulates cancelling an accepted booking. Verifies booking is deleted, notification is sent, and user is redirected. | ✅ |
| test\_check\_if\_matched\_true                  | Verifies the function returns `True` when both users like each other's profiles | ✅ |
| test\_check\_if\_matched\_false\_if\_one\_sided | Returns `False` if only one user liked the other                                | ✅ |
| test\_check\_if\_matched\_false\_if\_none       | Returns `False` if no mutual MatchResponses exist                               | ✅ |
| test\_user\_is\_matched\_true                        | Confirms mutual like returns `True`                    | ✅ |
| test\_user\_is\_matched\_false\_if\_one\_sided       | Returns `False` if only one user liked the other       | ✅ |
| test\_user\_is\_matched\_false\_if\_profile\_missing | Handles missing profile gracefully and returns `False` | ✅ |
| test_custom_logout_redirects_and_shows_message | Redirects to home and shows logout success message     | ✅ |
| test_custom_404_view_renders_template          | Returns custom 404 template with correct status code   | ✅ |
| test_about_page_get     | GET request to /about/ page                         | Returns 200 and uses 'about.html' template             | ✅ |
| test_about_form_valid_post | Submit valid contact form                          | Redirects to /about/, sends email, shows success alert | ✅ |
| test_about_form_invalid_post | Submit empty/invalid contact form                | No email sent, form errors displayed, error message shown | ✅ |

#### Messaging Models

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_create_message              | Verifies Message instance saves with correct fields| sender, recipient, content,                  |           |
|                                  |                                                    | timestamp are correct, __str__ format OK     | ✅        |
| test_create_booking_request | Creates a BookingRequest and verifies field values      | sender, recipient, message, default status,  |           |
|                              |                                                        |and string are correct                        |        ✅ |

#### Messaging Forms

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_valid_message_form          | Content filled in correctly                    | Form is valid                                    |     ✅    |
| test_blank_message_form          | No content submitted                           | Form is invalid, 'content' in errors             |     ✅    |
| test_message_widget_type         | Form uses Textarea with placeholder            | Placeholder is "Write your message..."           |     ✅    |
| test_valid_booking_request_form  | Proper date string submitted                   | Form is valid                                    |     ✅    |
| test_blank_booking_request_form  | No dates entered                               | Form is invalid, 'requested_dates' in errors     |     ✅    |
| test_requested_dates_widget_attrs | Widget has correct attributes (ID, placeholder) | Form input has expected HTML attributes        |     ✅    |

#### Notifications Models

| Test Name                        | Description                                        | Expected Result                                            | Pass/Fail |
|----------------------------------|----------------------------------------------------|------------------------------------------------------------|-----------|
| test_create_notification | Creates a Notification and verifies field values     | user, message, default is_read, and string representation are correct | ✅ |

#### Notifications Views Tests

| Test Name                        | Description                                        | Expected Result                                    | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_mark_all_read              | Marks all unread notifications as read via POST           | All user notifications are updated and redirected| ✅ |
| test_dismiss_notification       | Dismisses a single notification as read via POST          | Target notification `is_read=True`, redirected   | ✅ |
| test_mark_notification_read_with_link | Marks a notification read and redirects to its link | Notification updated and redirected to `link`    | ✅ |
| test_dismiss_notification_unauthorized_access | Tries to dismiss another user’s notification | 404 error returned                              | ✅ |

#### Notifications Context Processor

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_returns_queryset_for_authenticated_user | User with unread notifications  | QuerySet with correct length       | ✅ |
| test_returns_empty_queryset_if_all_read      | All notifications are read      | 	Empty QuerySet                    | ✅ |
| test_returns_empty_list_for_anonymous_user   | User not logged in              | Empty list returned                | ✅ |

#### Review Model

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_create_review                   | Creates a Review and verifies fields/str output       | Fields saved correctly and `__str__` is formatted       | ✅ |
| test_unique_reviewer_reviewee_constraint | Ensures a reviewer can’t submit two reviews for same user | Raises IntegrityError for duplicate pair        | ✅ |

#### Review Views

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_leave_review_post_valid        | Logged-in user submits a valid review for a matched user | Review saved, redirected to profile                        | ✅ |
| test_cannot_review_self            | User tries to review themselves                           | Error message shown, redirect back to profile              | ✅ |
| test_cannot_review_unmatched_user | User tries to review someone they haven't matched with    | Error message shown, no form shown                         | ✅ |
| test_delete_review                | User deletes their review via POST                        | Review removed, success message shown                      | ✅ |


#### Reviews Forms

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_form_valid_data         | Valid rating and comment submitted             | Form is valid                                          | ✅ |
| test_form_missing_rating     | No rating provided                             | Form is invalid, 'rating' in errors                    | ✅ |
| test_form_missing_comment    | No comment provided                            | Form is invalid, 'comment' in errors                   | ✅ |
| test_form_rating_choices     | Ensures custom radio choices are correctly set | Choices match 1–5 with star symbols                    | ✅ |
| test_form_labels             | Custom field labels applied                    | Label for rating is "Star Rating", comment is "Your Review" | ✅ |

## Lighthouse

I have used Googles Lighthouse testing to test the performance, accessibility, best practices and SEO of the site.

### Desktop Results

| Page | Result |
| :--- | :--- |
| Home Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\home-page-laptop-lighthouse.png) |
| About Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\about-page-laptop-lighthouse.png) |
| Travel Log Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\travel-log-laptop-lighthouse.png) |
| View Profile Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\view-profile-laptop-lighthouse.png) |
| Profile Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\profile-laptop-lighthouse.png) |
| Edit Profile Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\edit-profile-laptop-lighthouse.png) |
| Register Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\register-laptop-lighthouse.png) |
| Login Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\login-laptop-lighthouse.png) |

### Mobile Results

| Page | Result |
| :--- | :--- |
| Home Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\home-page-mobile-lighthouse.png) |
| About Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\about-page-mobile-lighthouse.png) |
| Travel Log Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\travel-log-mobile-lighthouse.png) |
| View Profile Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\view-profile-mobile-lighthouse.png) |
| Profile Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\profile-mobile-lighthouse.png) |
| Edit Profile Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\edit-profile-mobile-lighthouse.png) |
| Register Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\register-mobile-lighthouse.png) |
| Login Page | ![Home Desktop Lighthouse Testing](static\images\documentation\lighthouse\login-mobile-lighthouse.png) |

## Manual Testing

### 🔐 Authentication & Access Control

| Feature         | Scenario                               | Expected Result                   |           |
| --------------- | -------------------------------------- | --------------------------------- |           |
| Homepage access        | Non-user visits `/`              | Sees profile card                |    ✅     |
| Register form   | Submit incomplete or invalid data      | Validation errors shown           |    ✅     |
| Login           | User logs in with correct credentials  | Redirected to homepage/profile    |    ✅     | 
| Login fail      | User logs in with wrong password/email | Error message shown               |    ✅     |
| Protected pages | Access profile/edit while logged out   | Redirected to login with `?like=` |    ✅     |

### 🧾 Profile Features

| Feature      | Scenario                             | Expected Result             |          |
| ------------ | ------------------------------------ | --------------------------- |          |
| Edit profile | Update location and bio              | Changes saved and visible   |    ✅    |
| Upload image | Upload valid and invalid image types | Only valid formats accepted |    ✅    |
| Delete image | Delete a house image                 | Image removed from gallery  |    ✅    |

### 👍 Matching & Travel Log

| Feature              | Scenario                             | Expected Result                     |       |
| -------------------- | ------------------------------------ | ----------------------------------- |       |
| Like profile         | Logged-in user likes another profile | Profile saved to travel log         |   ✅  |
| Unlike profile       | Unlike a previously liked profile    | Removed from travel log             |   ✅  |
| Matched profile view | Access matched profile               | Can see calendar, messages, reviews |   ✅  |

### 📅 Booking System

| Feature              | Scenario                     | Expected Result                     |        |
| -------------------- | ---------------------------- | ---------------------------------   |        |
| Submit valid request | Pick available dates, submit | Request visible to recipient        |   ✅   |
| Respond to request   | Accept/ammend/decline a booking| Status changes, notification sent |   ✅   |
| View bookings        | View sent/received bookings  | Shows booking cards with status     |   ✅   |   

### 💬 Messaging & Notifications

| Feature              | Scenario                       | Expected Result                             |        |
| -------------------- | ------------------------------ | ------------------------------------------- |        |
| Send message         | Send a message to a match      | Message saved, shown in chat                |   ✅   |
| Receive notification | Matched user sees alert        | Alert appears in navbar/notification system |   ✅   |
| Clear notification   | Click on alert icon or message | Marked as read, no longer counted           |   ✅   |

### Admin Panel Testing

| Feature                  | Scenario                                                         | Expected Result                                        | Pass/Fail |
|--------------------------|------------------------------------------------------------------|--------------------------------------------------------|-----------|
| Admin access             | Superuser visits `/admin`                                       | Login page loads, admin access granted after login     |     ✅    |
| Profile management       | Admin views `Profile` list                                      | Usernames, visibility, and locations are shown         |     ✅    |
| Edit profile             | Admin edits a profile from admin panel                          | Form loads, changes are saved                          |     ✅    |
| MatchResponse visibility | Admin views user responses in `MatchResponse`                   | Shows sender, recipient, like/dislike status           |     ✅    |
| HouseImage management    | Admin sees images linked to profiles                            | Image records are viewable and deletable               |     ✅    |
| Review moderation        | Admin views and filters reviews by rating or user               | Reviewer, reviewee, rating, and comments are visible   |     ✅    |
| Notifications view       | Admin checks `Notification` model for user alerts               | User, message, read status, and timestamps visible     |     ✅    |
| Message tracking         | Admin browses `Message` records                                 | Sender, recipient, and content shown                   |     ✅    |
| BookingRequest tracking  | Admin views and filters bookings by status/date                 | Status (pending/accepted/etc.) and details are shown   |     ✅    |
| Search & filters         | Admin uses search fields in each model admin                    | Results filter by username or field as expected        |     ✅    |