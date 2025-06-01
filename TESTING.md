## Manual Testing Document

| Feature                | Scenario                         | Expected Result            | Pass/Fail |
|------------------------|----------------------------------|----------------------------|-----------|
| Homepage access        | Non-user visits `/`              | Sees profile card          |          |
| Like Profile button    | Guest user clicks 👍             | Prompted to login          |          | 
| Contact form           | Submit invalid email             | Validation error shown     |          |
| Booking calendar       | User selects unavailable dates   | Request not submitted      |          |

## Admin Panel Testing

| Feature                  | Scenario                                                         | Expected Result                                        | Pass/Fail |
|--------------------------|------------------------------------------------------------------|--------------------------------------------------------|-----------|
| Admin access             | Superuser visits `/admin`                                       | Login page loads, admin access granted after login     |           |
| Profile management       | Admin views `Profile` list                                      | Usernames, visibility, and locations are shown         |           |
| Edit profile             | Admin edits a profile from admin panel                          | Form loads, changes are saved                          |           |
| MatchResponse visibility | Admin views user responses in `MatchResponse`                   | Shows sender, recipient, like/dislike status           |           |
| HouseImage management    | Admin sees images linked to profiles                            | Image records are viewable and deletable               |           |
| Review moderation        | Admin views and filters reviews by rating or user               | Reviewer, reviewee, rating, and comments are visible   |           |
| Notifications view       | Admin checks `Notification` model for user alerts               | User, message, read status, and timestamps visible     |           |
| Message tracking         | Admin browses `Message` records                                 | Sender, recipient, and content shown                   |           |
| BookingRequest tracking  | Admin views and filters bookings by status/date                 | Status (pending/accepted/etc.) and details are shown   |           |
| Search & filters         | Admin uses search fields in each model admin                    | Results filter by username or field as expected        |           |

## Profiles Tests

### Models Tests

| Test Name               | Description                                                  | Expected Result                              | Pass/Fail |
|-------------------------|--------------------------------------------------------------|-----------------------------------------------|-----------|
| test_profile_creation   | Verifies that a Profile instance returns the correct string | `__str__()` returns "username - location"     | ✅         |
| test_profile_creation | Profile string shows "username - location"            | `__str__()` returns correct string                    | ✅         |
| test_valid_image      | Validates small JPEG image passes validation          | No exception raised                                   | ✅         |
| test_invalid_type     | Validates .gif image is rejected                      | Raises ValidationError                                | ✅         |
| test_too_large_image  | Validates oversized JPEG is rejected                  | Raises ValidationError                                | ✅         |
| test_house_image_creation | Validates that a HouseImage links to profile and saves | Profile is linked, `is_main=True`, string correct | ✅       |
| test_create_match_response       | Creates a MatchResponse and links users                  | Fields are correctly assigned                | ✅         |
| test_str_method                  | Checks __str__ shows "liked/disliked" format             | String returns "user1 disliked user2"        | ✅         |
| test_unique_together_constraint | Ensures same user can't rate same profile twice          | Second response raises IntegrityError/Exception | ✅     |

### Views Tests

| Test Name                    | Description                                  | Expected Result                             | Pass/Fail |
|------------------------------|----------------------------------------------|----------------------------------------------|-----------|
| test_redirect_if_not_logged_in | Anonymous user is redirected to login       | Redirect with ?next=/profile/                | ✅         |
| test_profile_view_authenticated | Logged-in user sees profile, template loads | 200 response, context populated              | ✅         |

### Edit Profile View Tests

| Test Name                      | Description                                         | Expected Result                              | Pass/Fail |
|--------------------------------|-----------------------------------------------------|-----------------------------------------------|-----------|
| test_redirect_if_not_logged_in | Redirects unauthenticated users                    | Redirects to login with `?next=`              | ✅         |
| test_get_request_renders_forms | Loads edit_profile template and prepopulated forms | Form instances and profile appear in context | ✅         |
| test_post_valid_data_updates_profile | Valid form data saves and redirects             | Profile is updated and success message shown | ✅         |

### Set Main Image View Tests

| Test Name                 | Description                                 | Expected Result                         | Pass/Fail |
|---------------------------|---------------------------------------------|------------------------------------------|-----------|
| test_redirect_if_not_logged_in | Redirects anonymous users                | Redirects to login page                  | ✅         |
| test_set_main_image       | Sets selected image as main, clears previous | is_main updated, redirects to edit page | ✅         |

### Upload Images View Tests

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_redirect_if_not_logged_in   | Anonymous user is blocked                         | Redirects to login                           | ✅         |
| test_upload_single_image_auto_sets_main | First image uploaded becomes main image    | One image saved, marked is_main=True         | ✅         |
| test_upload_sets_manual_main_image | User selects main image via POST param         | Selected image set as main                   | ✅         |

### Messaging Tests

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_create_message              | Verifies Message instance saves with correct fields| sender, recipient, content,                  |           |
|                                  |                                                    | timestamp are correct, __str__ format OK     | ✅        |
| test_create_booking_request | Creates a BookingRequest and verifies field values      | sender, recipient, message, default status,  |           |
|                              |                                                        |and string are correct                        |        ✅ |
