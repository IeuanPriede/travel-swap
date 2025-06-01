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

### Profiles Models 

| test_profile_str                             | Profile with user and country               | Returns 'username - country'                      | ✅ |
| test_profile_defaults                        | Profile created without optional fields     | is_visible=True and blank fields are allowed      | ✅ |
| test_house_image_str                         | HouseImage linked to profile                | Returns 'Image for username'                      | ✅ |
| test_image_validator_rejects_large_file      | Upload file >2MB                            | Raises ValidationError                            | ✅ |
| test_image_validator_rejects_invalid_type    | Upload file with invalid MIME type          | Raises ValidationError                            | ✅ |
| test_match_response_str                      | MatchResponse for a like/dislike            | Returns 'user liked/disliked user'                | ✅ |
| test_match_response_unique_constraint        | Duplicate like by same user to same profile | Raises IntegrityError due to unique_together rule | ✅ |

### Profiles Forms

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

### Profiles Views

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



## Messaging

### Messaging Models

| Test Name                        | Description                                        | Expected Result                             | Pass/Fail |
|----------------------------------|----------------------------------------------------|----------------------------------------------|-----------|
| test_create_message              | Verifies Message instance saves with correct fields| sender, recipient, content,                  |           |
|                                  |                                                    | timestamp are correct, __str__ format OK     | ✅        |
| test_create_booking_request | Creates a BookingRequest and verifies field values      | sender, recipient, message, default status,  |           |
|                              |                                                        |and string are correct                        |        ✅ |

### Messaging Forms

| test_valid_message_form          | Content filled in correctly                    | Form is valid                              | ✅ |
| test_blank_message_form          | No content submitted                           | Form is invalid, 'content' in errors        | ✅ |
| test_message_widget_type         | Form uses Textarea with placeholder            | Placeholder is "Write your message..."      | ✅ |
| test_valid_booking_request_form  | Proper date string submitted                   | Form is valid                              | ✅ |
| test_blank_booking_request_form  | No dates entered                               | Form is invalid, 'requested_dates' in errors | ✅ |
| test_requested_dates_widget_attrs | Widget has correct attributes (ID, placeholder) | Form input has expected HTML attributes     | ✅ |

## Notifications

### Notifications Models

| test_create_notification | Creates a Notification and verifies field values     | user, message, default is_read, and string representation are correct | ✅ |

### Notifications Views Tests

| test_mark_all_read              | Marks all unread notifications as read via POST           | All user notifications are updated and redirected| ✅ |
| test_dismiss_notification       | Dismisses a single notification as read via POST          | Target notification `is_read=True`, redirected   | ✅ |
| test_mark_notification_read_with_link | Marks a notification read and redirects to its link | Notification updated and redirected to `link`    | ✅ |
| test_dismiss_notification_unauthorized_access | Tries to dismiss another user’s notification | 404 error returned                              | ✅ |

### Notifications Context Processor

| test_returns_queryset_for_authenticated_user | User with unread notifications  | QuerySet with correct length       | ✅ |
| test_returns_empty_queryset_if_all_read      | All notifications are read      | 	Empty QuerySet                    | ✅ |
| test_returns_empty_list_for_anonymous_user   | User not logged in              | Empty list returned                | ✅ |

## Reviews

### Review Model

| test_create_review                   | Creates a Review and verifies fields/str output       | Fields saved correctly and `__str__` is formatted       | ✅ |
| test_unique_reviewer_reviewee_constraint | Ensures a reviewer can’t submit two reviews for same user | Raises IntegrityError for duplicate pair        | ✅ |

### Review Views

| test_leave_review_post_valid        | Logged-in user submits a valid review for a matched user | Review saved, redirected to profile                        | ✅ |
| test_cannot_review_self            | User tries to review themselves                           | Error message shown, redirect back to profile              | ✅ |
| test_cannot_review_unmatched_user | User tries to review someone they haven't matched with    | Error message shown, no form shown                         | ✅ |
| test_delete_review                | User deletes their review via POST                        | Review removed, success message shown                      | ✅ |


### Reviews Forms

| test_form_valid_data         | Valid rating and comment submitted             | Form is valid                                          | ✅ |
| test_form_missing_rating     | No rating provided                             | Form is invalid, 'rating' in errors                    | ✅ |
| test_form_missing_comment    | No comment provided                            | Form is invalid, 'comment' in errors                   | ✅ |
| test_form_rating_choices     | Ensures custom radio choices are correctly set | Choices match 1–5 with star symbols                    | ✅ |
| test_form_labels             | Custom field labels applied                    | Label for rating is "Star Rating", comment is "Your Review" | ✅ |
