from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile, HouseImage, MatchResponse
from .forms import (
    CustomUserCreationForm,
    ProfileForm,
    UserForm,
    ImageFormSet,
    SearchForm,
    ContactForm,
)
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from cloudinary.uploader import destroy
from django.template.loader import render_to_string
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Avg
from messaging.forms import MessageForm, BookingRequestForm
from messaging.models import Message, BookingRequest
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import datetime
import logging
from django.urls import reverse
from notifications.models import Notification
from reviews.forms import ReviewForm
from reviews.models import Review


# View to display the logged-in user's profile
@login_required
def profile_view(request):
    # Get or create a Profile instance tied to the logged-in user
    profile, created = Profile.objects.get_or_create(user=request.user)
    house_images = profile.house_images.all()
    reviews = Review.objects.filter(reviewee=request.user)
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    # Pass profile object to the template
    return render(request, 'profiles/profile.html', {
        'profile': profile,
        'house_images': house_images,
        'reviews': reviews,
        'average_rating': round(average_rating, 1) if average_rating else None,
        })


# Edit profile view
@login_required
def edit_profile(request):
    # Get the current user's profile
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        print("Form submitted")
        # Handle the form submission
        user_form = UserForm(
            request.POST, instance=request.user
            )  # for updating the user model
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=profile
            )  # for updating the profile model
        formset = ImageFormSet(
            request.POST,
            request.FILES,
            queryset=HouseImage.objects.filter(profile=profile)
        )

        print("Formset data:", request.POST)
        total_forms = request.POST.get('form-TOTAL_FORMS')
        initial_forms = request.POST.get('form-INITIAL_FORMS')
        print("Management form data:", total_forms, initial_forms)

        # Check all forms individually first
        user_form_valid = user_form.is_valid()
        profile_form_valid = profile_form.is_valid()
        formset_valid = formset.is_valid()

        # Debug: print validation states
        print(
            "DEBUG - Form valid states:",
            user_form_valid, profile_form_valid
        )
        print("UserForm errors:", user_form.errors)
        print("ProfileForm errors:", profile_form.errors)
        print("Formset valid:", formset_valid)
        print("Formset errors:", formset.errors)

        if user_form_valid and profile_form_valid and formset_valid:
            print("All forms valid")
            user_form.save()
            profile_form.save()

            images = formset.save(commit=False)
            for image in images:
                if image.image:  # only save if image was uploaded
                    image.profile = profile
                    image.save()

            formset.save_m2m()

            messages.success(request, "Your profile has been updated.")
            return redirect(
                'profiles'
                )  # Redirect to the profile view after successful update
    else:
        user_form = UserForm(
            instance=request.user
            )  # Prepopulate with current user info
        profile_form = ProfileForm(
            instance=profile
            )  # Prepopulate with current profile info
        formset = ImageFormSet(
            queryset=HouseImage.objects.filter(profile=profile)
            )

    return render(request, 'profiles/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'formset': formset,
        'profile': profile,
    })


@login_required
def upload_images(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        formset = ImageFormSet(
            request.POST, request.FILES, queryset=HouseImage.objects.none())

        for form in formset:
            print("Form cleaned data:", getattr(form, 'cleaned_data', {}))
            print("Form errors:", form.errors)
            if not form.has_changed():
                form.empty_permitted = True

        if formset.is_valid():
            new_images = []

            for form in formset:
                image_file = form.cleaned_data.get('image')
                if image_file:
                    instance = form.save(commit=False)
                    instance.profile = profile
                    try:
                        instance.save()
                        new_images.append(instance)
                    except Exception as e:
                        print("Upload failed:", e)
                        messages.error(request, f"Image upload failed: {e}")
                        return render(request, 'profiles/edit_profile.html', {
                            'user_form': UserForm(instance=request.user),
                            'profile_form': ProfileForm(instance=profile),
                            'formset': formset,
                            'profile': profile,
                        })

            messages.success(request, "Images updated successfully.")
            return redirect('edit_profile')

        else:
            messages.error(request, "There was a problem updating images.")
            return render(request, 'profiles/edit_profile.html', {
                'user_form': UserForm(instance=request.user),
                'profile_form': ProfileForm(instance=profile),
                'formset': formset,
                'profile': profile,
            })

    return redirect('edit_profile')


@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your profile has been deleted.")
        return redirect('home')
    return redirect('edit_profile')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profiles')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def delete_image(request, image_id):
    print(f"Delete request received for image_id={image_id}")

    image = get_object_or_404(HouseImage, id=image_id)

    if image.profile.user != request.user:
        print("Forbidden: user mismatch")
        return JsonResponse({"error": "Forbidden"}, status=403)

    if request.method == "POST":
        public_id = image.image.name.rsplit('.', 1)[0]
        print(f"Deleting Cloudinary image: public_id={public_id}")
        try:
            destroy(public_id)
        except Exception as e:
            print(f"Error deleting image from Cloudinary: {e}")

        image.delete()
        print("Image deleted successfully")
        return HttpResponse(status=204)  # ✅ No content

    print("Invalid request method")
    return JsonResponse({"error": "Invalid request"}, status=400)


def home(request):
    profiles = Profile.objects.filter(is_visible=True)
    form = SearchForm(request.GET or None)

    # Get the IDs of profiles the user already responded to
    if request.user.is_authenticated:
        # Logged-in users: exclude their own and previously responded profiles
        responded_ids = MatchResponse.objects.filter(
            from_user=request.user
        ).values_list('to_profile_id', flat=True)

        profiles = Profile.objects.filter(
            ~Q(user=request.user),
            is_visible=True
        ).exclude(id__in=responded_ids)

    if form.is_valid():
        for field, value in form.cleaned_data.items():
            if value:
                profiles = profiles.filter(**{field: True})

    # Date range filtering (outside of the SearchForm)
    date_range = request.GET.get("dates")
    if date_range:
        try:
            start_date, end_date = date_range.split(" to ")
            profiles = profiles.filter(
                available_dates__icontains=start_date
            ) | profiles.filter(
                available_dates__icontains=end_date
            )
        except ValueError:
            pass  # If the input isn't a valid date range string

    else:
        # Guest users: show only visible profiles (basic demo mode)
        profiles = Profile.objects.filter(is_visible=True)

    # Get the first profile from the filtered list
    next_profile = profiles.first()
    reviews = []
    average_rating = None

    if next_profile:
        reviews = Review.objects.filter(reviewee=next_profile.user)
        average_rating_val = reviews.aggregate(avg=Avg('rating'))['avg']
        average_rating = (
            round(average_rating_val, 1) 
            if average_rating_val else None
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/profile_card.html', {
            'profile': next_profile,
            'reviews': reviews,
            'average_rating': average_rating,
        }, request=request)
        return JsonResponse({'next_profile_html': html})

    return render(request, 'home.html', {
        'profile': next_profile,
        'form': form,  # pass form to template
        'reviews': reviews,
        'average_rating': average_rating,
    })


@csrf_exempt
def next_profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        profile_id = data.get('profile_id')
        profile = get_object_or_404(Profile, id=profile_id)

        skipped_ids = request.session.get('skipped_profiles', [])
        responded_ids = []

        skipped_ids.append(profile.id)
        request.session['skipped_profiles'] = skipped_ids

        if request.user.is_authenticated:
            responded_ids = MatchResponse.objects.filter(
                from_user=request.user
            ).values_list('to_profile_id', flat=True)

        next_profile = Profile.objects.filter(
            is_visible=True
        ).exclude(id__in=responded_ids).exclude(id__in=skipped_ids).first()

        if next_profile:
            html = render_to_string('partials/profile_card.html', {
                'profile': next_profile
            }, request=request)
        else:
            html = "<p class='text-center mt-5'>🎉 "
            "No more profiles available!</p>"

        return JsonResponse({
            'match': False,
            'next_profile_html': html
        })


@csrf_exempt
@login_required
def like_profile(request):
    print("DEBUG - Like recorded by:", request.user.username)
    if request.method == 'POST':
        data = json.loads(request.body)
        profile_id = data.get('profile_id')
        profile = get_object_or_404(Profile, id=profile_id)

        # Create or update MatchResponse
        match, created = MatchResponse.objects.get_or_create(
            from_user=request.user,
            to_profile=profile,
            defaults={'liked': True}
        )

        if not created and not match.liked:
            match.liked = True
            match.save()

        # Check if it's a mutual match
        is_match = MatchResponse.objects.filter(
            from_user=profile.user,
            to_profile__user=request.user,
            liked=True
        ).exists()

        email_logger = logging.getLogger('email_notifications')

        # ✅ Send email if a mutual match is confirmed
        if is_match:
            send_mail(
                subject="You've got a new match on TravelSwap!",
                message=(
                    f"You and {profile.user.username} "
                    "have liked each other.\n\n"
                    "Visit their profile to start "
                    "messaging or suggest vacation dates."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
            send_mail(
                subject="You've got a new match on TravelSwap!",
                message=(
                    f"{request.user.username} also liked you back!\n\n"
                    "Log in to view their profile and connect."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.user.email],
                fail_silently=False,
            )
            email_logger.info(
                f"Match email sent to: {profile.user.email} "
                "with subject: {subject}"
            )
            matched_profile_url = reverse(
                'view_profile', args=[profile.user.id])
            messages.info(
                request,
                f"You've matched with {profile.user.username}! "
                f"<a href='{matched_profile_url}'>View profile</a>"
            )
            Notification.objects.create(
                user=profile.user,
                message=f"You matched with {request.user.username}!",
                link=reverse('view_profile', args=[request.user.id])
            )
            Notification.objects.create(
                user=request.user,
                message=f"You matched with {profile.user.username}!",
                link=reverse('view_profile', args=[profile.user.id])
            )

        # Get next profile to show
        next_profile = Profile.objects.exclude(user=request.user).exclude(
            id__in=MatchResponse.objects.filter(
                from_user=request.user
            ).values_list('to_profile_id', flat=True)
        ).first()

        html = render_to_string('partials/profile_card.html', {
            'profile': next_profile}, request=request)

        return JsonResponse({
            'match': is_match,
            'match_with': profile.user.username if is_match else None,
            'next_profile_html': html
        })


@login_required
def travel_log(request):
    liked_profiles = MatchResponse.objects.filter(
        from_user=request.user,
        liked=True,
        to_profile__user__isnull=False  # ensures the profile has a user
    ).select_related('to_profile', 'to_profile__user')

    # Build mutual match list (by setting a flag on each match)
    for match in liked_profiles:
        is_mutual = MatchResponse.objects.filter(
            from_user=match.to_profile.user,
            to_profile__user=request.user,
            liked=True
        ).exists()
        match.is_mutual = is_mutual  # attach flag directly

    mutual_matches_count = sum(
        1 for match in liked_profiles if match.is_mutual)

    return render(request, 'travel_log.html', {
        'liked_profiles': liked_profiles,
        'mutual_matches_count': mutual_matches_count,
    })


@login_required
def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    profile = Profile.objects.get(user=profile_user)
    is_match = check_if_matched(request.user, profile_user)
    user_is_viewing_own = request.user == profile_user
    can_review = is_match and not user_is_viewing_own

    # Handle Review logic
    existing_review = Review.objects.filter(
        reviewer=request.user, reviewee=profile_user).first()
    review_form = ReviewForm(instance=existing_review) if can_review else None

    message_form = None
    messages_between = None

    if is_match:
        messages_between = Message.objects.filter(
            Q(sender=request.user, recipient=profile_user) |
            Q(sender=profile_user, recipient=request.user)
        ).order_by('timestamp')

        if request.method == 'POST':
            message_form = MessageForm(request.POST)
            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.sender = request.user
                message.recipient = profile_user
                message.save()

                send_mail(
                    subject=f'New message from {request.user.username} '
                    'on TravelSwap!',
                    message=(
                        f"You've received a new message from {
                            request.user.username}:\n\n"
                        f"{message.content}\n\n"
                        "Log in to TravelSwap to view and reply."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[profile_user.email],
                    fail_silently=False,
                )

                messages.success(request, "Message sent successfully!")
                return redirect('view_profile', user_id=profile_user.id)
            print("Messages:", messages.get_messages(request))
        else:
            message_form = MessageForm()

    profile = Profile.objects.get(user=profile_user)

    booking = BookingRequest.objects.filter(
        Q(sender=request.user, recipient=profile_user) |
        Q(sender=profile_user, recipient=request.user)
    ).order_by('-created_at').first()

    available_start = None
    available_end = None

    if profile.available_dates and 'to' in profile.available_dates:
        try:
            start_str, end_str = profile.available_dates.split(' to ')
            available_start = datetime.strptime(
                start_str.strip(), '%Y-%m-%d').date()
            available_end = datetime.strptime(
                end_str.strip(), '%Y-%m-%d').date()
        except ValueError:
            pass

    if request.method == 'POST' and 'request_booking' in request.POST:
        booking_form = BookingRequestForm(request.POST)
        if booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.sender = request.user
            booking.recipient = profile_user
            booking.created_at = now()
            booking.last_action_by = request.user
            booking.save()
            Notification.objects.create(
                user=profile_user,
                message=f"{request.user.username} "
                "sent you a vacation exchange request.",
                link=reverse('view_profile', args=[request.user.id])
            )
            print("✅ Notification created for:", profile_user.username)
            send_mail(
                subject='New vacation exchange request on TravelSwap',
                message=(
                    f"{request.user.username} has requested "
                    "a vacation exchange with you.\n\n"
                    f"Dates: {booking.requested_dates}\n\n"
                    "Log in to your account to respond."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile_user.email],
                fail_silently=False,
            )
            messages.success(request, "Booking request sent!")
            return redirect('view_profile', user_id=profile_user.id)

    elif (
        request.method == 'POST'
        and 'respond_booking' in request.POST
        and booking
    ):
        action = request.POST.get('respond_booking')

        recipient = (
            booking.recipient
            if booking.recipient != request.user
            else booking.sender
        )

        if action == 'amended':
            new_dates = request.POST.get('amended_dates')
            if new_dates:
                booking.requested_dates = new_dates
                send_mail(
                    subject='Booking request amended',
                    message=(
                        f"{request.user.username} has suggested "
                        "new dates for your vacation exchange.\n\n"
                        f"Suggested Dates: {new_dates}\n\n"
                        "Log in to respond to the update."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                Notification.objects.create(
                    user=recipient,
                    message=f"{request.user.username} suggested "
                    "new vacation dates.",
                    link=reverse('view_profile', args=[request.user.id])
                )

        if action in ['accepted', 'amended', 'denied']:
            booking.status = action
            booking.responded_at = now()
            booking.last_action_by = request.user
            booking.save()

            if action in ['accepted', 'denied']:
                send_mail(
                    subject=f"Booking request {action} on TravelSwap",
                    message=(
                        f"{request.user.username} has {action} "
                        "your vacation exchange request.\n\n"
                        f"Dates: {booking.requested_dates}\n\n"
                        "Log in to see details."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                Notification.objects.create(
                    user=recipient,
                    message=f"{request.user.username} {action} "
                    "your vacation request.",
                    link=reverse('view_profile', args=[request.user.id])
                )

            print("✅ Notification created for:", recipient.username)
            print("🔔 Now unread for them:", Notification.objects.filter(
                user=recipient, is_read=False).count())

            messages.success(request, f"Request {action}.")
            return redirect('view_profile', user_id=profile_user.id)

    elif 'cancel_booking' in request.POST and booking:
        booking.delete()
        messages.success(request, "Vacation exchange cancelled.")
        return redirect('view_profile', user_id=profile_user.id)

    elif 'submit_review' in request.POST and can_review:
        review_form = ReviewForm(request.POST, instance=existing_review)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.reviewer = request.user
            review.reviewee = profile_user
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('view_profile', user_id=profile_user.id)

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'is_match': is_match,
        'message_form': message_form,
        'messages_between': messages_between,
        'booking': booking,
        'available_start': available_start,
        'available_end': available_end,
        'can_review': can_review,
        'review_form': review_form,
        'existing_review': existing_review,
        'reviews': Review.objects.filter(reviewee=profile_user),
    }
    print("🔔 Unread notifications for this user:",
          Notification.objects.filter(
              user=request.user, is_read=False).count())

    return render(request, 'profiles/view_profile.html', context)


def check_if_matched(user1, user2):
    return MatchResponse.objects.filter(
        from_user=user1,
        to_profile__user=user2,
        liked=True
    ).exists() and MatchResponse.objects.filter(
        from_user=user2,
        to_profile__user=user1,
        liked=True
    ).exists()


def user_is_matched(user1, user2):
    try:
        profile2 = user2.profile
        profile1 = user1.profile
        liked_by_user1 = MatchResponse.objects.filter(
            from_user=user1, to_profile=profile2, liked=True).exists()
        liked_by_user2 = MatchResponse.objects.filter(
            from_user=user2, to_profile=profile1, liked=True).exists()
        return liked_by_user1 and liked_by_user2
    except Profile.DoesNotExist:
        return False


def about(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                cd['subject'],
                cd['message'],
                cd['email'],
                [settings.DEFAULT_FROM_EMAIL],  # or a dedicated admin email
            )
            messages.success(request, "Your message has been sent!")
            return redirect('about')  # redirects back to about page
    else:
        form = ContactForm()
    return render(request, 'about.html', {'form': form})


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')
