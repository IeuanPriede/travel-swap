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
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
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
import random
from django.urls import reverse
from notifications.models import Notification
from reviews.forms import ReviewForm
from reviews.models import Review
from django_countries import countries
from django.http import HttpResponseNotAllowed


# View to display the logged-in user's profile
@login_required
def profile_view(request):
    # Get or create a Profile instance tied to the logged-in user
    profile, created = Profile.objects.get_or_create(user=request.user)
    print("DEBUG: Profile location is:", profile.location)
    house_images = profile.house_images.all()
    reviews = Review.objects.filter(reviewee=request.user)
    average_rating_val = reviews.aggregate(avg=Avg('rating'))['avg']
    average_rating = float(average_rating_val) if average_rating_val else None
    # Pass profile object to the template
    return render(request, 'profiles/profile.html', {
        'profile': profile,
        'house_images': house_images,
        'reviews': reviews,
        'average_rating': round(average_rating, 1) if average_rating else None,
        })


@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        print("Form submitted")
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=profile)

        user_form_valid = user_form.is_valid()
        profile_form_valid = profile_form.is_valid()

        print("DEBUG - Form valid states:",
              user_form_valid, profile_form_valid)
        print("UserForm errors:", user_form.errors)
        print("ProfileForm errors:", profile_form.errors)

        if user_form_valid and profile_form_valid:
            print("User and Profile forms are valid")
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profiles')

        # If validation fails, re-render the form with errors
        formset = ImageFormSet(
            queryset=HouseImage.objects.filter(profile=profile))

    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
        formset = ImageFormSet(
            queryset=HouseImage.objects.filter(profile=profile))

    return render(request, 'profiles/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'formset': formset,  # for image modal only
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
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            request.user.delete()
            messages.success(request, "Your profile has been deleted.")
            return redirect('home')
        else:
            messages.error(request, "Incorrect password. Please try again.")
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
    form = SearchForm(request.GET or None)
    profiles = Profile.objects.filter(is_visible=True)

    # Get list of profiles the user has already responded to
    responded_ids = []
    if request.user.is_authenticated:
        responded_ids = MatchResponse.objects.filter(
            from_user=request.user
        ).values_list('to_profile_id', flat=True)
        profiles = profiles.exclude(user=request.user)
    else:
        # If not authenticated,
        # still try to exclude anonymous user profile if any
        profiles = profiles.exclude(user__isnull=True)

    profiles = profiles.exclude(id__in=responded_ids)

    # Apply house criteria filters from form
    if form.is_valid():
        for field, value in form.cleaned_data.items():
            if value and field != "location":
                profiles = profiles.filter(**{field: True})
        if form.cleaned_data.get("location"):
            profiles = profiles.filter(location=form.cleaned_data["location"])

    # Apply date range filter
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
            pass

    # Create randomized profile sequence on first load
    profile_ids = list(profiles.values_list('id', flat=True))
    random.shuffle(profile_ids)
    request.session['profile_sequence'] = profile_ids
    request.session['current_index'] = 0

    # Load the first profile
    next_profile = None
    if profile_ids:
        next_profile = Profile.objects.get(id=profile_ids[0])
        request.session['current_index'] = 1

    reviews = []
    average_rating = None

    if next_profile:
        reviews = Review.objects.filter(reviewee=next_profile.user)
        average_rating_val = reviews.aggregate(avg=Avg('rating'))['avg']
        if average_rating_val:
            average_rating = round(average_rating_val, 1)

    # AJAX: return partial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/profile_card.html', {
            'profile': next_profile,
            'reviews': reviews,
            'average_rating': average_rating,
        }, request=request)
        return JsonResponse({'next_profile_html': html})

    # Normal page load
    return render(request, 'home.html', {
        'profile': next_profile,
        'form': form,
        'reviews': reviews,
        'average_rating': average_rating,
        'countries': list(countries),
    })


def next_profile(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body)
    filters = data.get('filters', {})

    profile_ids = request.session.get('profile_sequence', [])
    current_index = request.session.get('current_index', 0)

    # If we reached the end, reshuffle and restart
    if current_index >= len(profile_ids):

        # ✅ Prevent infinite loop if only one profile matches
        if len(profile_ids) == 1:
            html = (
                "<div class='alert alert-info text-center mt-4'>"
                "🎉 You've already seen the only matching profile. "
                "Try changing your filters to see more!</div>"
            )
            return JsonResponse(
                {'match': False, 'next_profile_html': html})
        profiles = Profile.objects.filter(is_visible=True)

        if request.user.is_authenticated:
            profiles = profiles.exclude(user=request.user)
            responded_ids = MatchResponse.objects.filter(
                from_user=request.user
            ).values_list('to_profile_id', flat=True)
            profiles = profiles.exclude(id__in=responded_ids)
        else:
            profiles = profiles.exclude(user__isnull=True)

        # Re-apply filters
        form = SearchForm(filters)
        if form.is_valid():
            for field, value in form.cleaned_data.items():
                if value and field != "location":
                    profiles = profiles.filter(**{field: True})
            if form.cleaned_data.get("location"):
                profiles = profiles.filter(
                    location=form.cleaned_data["location"])

        profile_ids = list(profiles.values_list('id', flat=True))
        random.shuffle(profile_ids)
        current_index = 0
        request.session['profile_sequence'] = profile_ids
        request.session['current_index'] = current_index

    # Try to get the next profile
    next_profile = None
    if current_index < len(profile_ids):
        try:
            next_profile = Profile.objects.get(
                id=profile_ids[current_index])
            request.session['current_index'] = current_index + 1
        except Profile.DoesNotExist:
            next_profile = None

    # Prepare HTML
    if next_profile:
        reviews = Review.objects.filter(reviewee=next_profile.user)
        avg_val = reviews.aggregate(avg=Avg('rating'))['avg']
        average_rating = round(avg_val, 1) if avg_val else None

        html = render_to_string('partials/profile_card.html', {
            'profile': next_profile,
            'reviews': reviews,
            'average_rating': average_rating,
        }, request=request)
    else:
        html = (
            "<p class='text-center mt-5'>🎉 "
            "No more profiles available!</p>"
        )

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
        print("✅ Like profile view hit for:", profile.user.username)

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

        print("Returning JSON with message:", (
                f"You matched with {profile.user.username}! 🎉"
                if is_match else
                f"You liked {profile.user.username}'s profile."
            ))

        return JsonResponse({
            'match': is_match,
            'match_with': profile.user.username if is_match else None,
            'next_profile_html': html,
            'message': (
                f"You matched with {profile.user.username}! 🎉"
                if is_match else
                f"You liked {profile.user.username}'s profile."
            )
        })


@login_required
def unlike_profile(request, profile_id):
    try:
        match = MatchResponse.objects.get(
            from_user=request.user,
            to_profile_id=profile_id,
            liked=True
        )
        username = match.to_profile.user.username
        match.delete()
        messages.success(
            request, f"You have unliked {username}'s profile.")
    except MatchResponse.DoesNotExist:
        messages.warning(
            request, f"You haven't {username}'s profile.")

    return HttpResponseRedirect(reverse('travel_log'))


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
    booking_form = None

    if is_match:
        messages_between = Message.objects.filter(
            Q(sender=request.user, recipient=profile_user) |
            Q(sender=profile_user, recipient=request.user)
        ).order_by('timestamp')

        if request.method == 'POST' and 'content' in request.POST:
            message_form = MessageForm(request.POST)

            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.sender = request.user
                message.recipient = profile_user
                message.save()

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'username': request.user.username,
                        'content': message.content,
                    })

                send_mail(
                    subject=f'New message from {request.user.username} '
                    'on TravelSwap!',
                    message=(
                        f"You've received a new message from "
                        f"{request.user.username}:\n\n"
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

    if request.method == 'POST':
        if 'request_booking' in request.POST:
            result = handle_booking_request(request, profile_user)
            if result:
                return result

        elif 'respond_booking' in request.POST and booking:
            result = handle_booking_response(request, profile_user, booking)
            if result:
                return result

        elif 'cancel_booking' in request.POST and booking:
            return handle_booking_cancel(request, profile_user, booking)

        elif 'submit_review' in request.POST and can_review:
            review_form = ReviewForm(request.POST, instance=existing_review)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.reviewer = request.user
                review.reviewee = profile_user
                review.save()
                messages.success(request, "Your review has been submitted.")
                return redirect('view_profile', user_id=profile_user.id)

    if is_match:
        if request.method == 'POST' and 'request_booking' in request.POST:
            booking_form = BookingRequestForm(request.POST)
        else:
            booking_form = BookingRequestForm()

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
        'booking_form': booking_form,
    }
    print("🔔 Unread notifications for this user:",
          Notification.objects.filter(
              user=request.user, is_read=False).count())

    return render(request, 'profiles/view_profile.html', context)


def get_latest_booking(user, other_user):
    return BookingRequest.objects.filter(
        Q(sender=user, recipient=other_user) |
        Q(sender=other_user, recipient=user)
    ).order_by('-created_at').first()


def handle_booking_request(request, profile_user):
    form = BookingRequestForm(request.POST)
    if form.is_valid():
        booking = form.save(commit=False)
        booking.sender = request.user
        booking.recipient = profile_user
        booking.created_at = now()
        booking.last_action_by = request.user
        booking.save()

        Notification.objects.create(
            user=profile_user,
            message=f"{request.user.username} "
                    f"sent you a vacation exchange request.",
            link=reverse('view_profile', args=[request.user.id])
        )

        send_mail(
            subject='New vacation exchange request on TravelSwap',
            message=f"{request.user.username} "
                    f"has requested a vacation exchange.\n\n"
                    f"Dates: {booking.requested_dates}\n\n"
                    "Log in to your account to respond.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile_user.email],
            fail_silently=False,
        )

        messages.success(request, "Booking request sent!")
        return redirect('view_profile', user_id=profile_user.id)
    return None


def handle_booking_response(request, profile_user, booking):
    action = request.POST.get('respond_booking')
    if booking.recipient != request.user:
        recipient = booking.recipient
    else:
        recipient = booking.sender

    if action == 'amended':
        new_dates = request.POST.get('amended_dates')
        if new_dates:
            booking.requested_dates = new_dates
            send_mail(
                subject='Booking request amended',
                message=(
                    f"{request.user.username} has suggested new dates.\n\n"
                    f"Suggested Dates: {new_dates}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            Notification.objects.create(
                user=recipient,
                message=f"{request.user.username} "
                        f"suggested new vacation dates.",
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
                message=f"{request.user.username} has "
                        f"{action} your vacation request.\n\n"
                        f"Dates: {booking.requested_dates}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            Notification.objects.create(
                user=recipient,
                message=f"{request.user.username} {action} "
                        f"your vacation request.",
                link=reverse('view_profile', args=[request.user.id])
            )

        # Flash message to current user
        if action == 'accepted':
            messages.success(request, "Vacation request accepted!")
        elif action == 'denied':
            if booking.sender == request.user:
                messages.warning(request, "Your vacation request was denied.")
            else:
                messages.info(request, f"You denied the request from "
                              f"{booking.sender.username}.")
        elif action == 'amended':
            messages.info(request, "You proposed new dates.")

        return redirect('view_profile', user_id=profile_user.id)
    return None


def handle_booking_cancel(request, profile_user, booking):
    # Identify the other user
    if booking.sender == request.user:
        recipient = booking.recipient
    else:
        recipient = booking.sender

    # Store the dates before deleting
    cancelled_dates = booking.requested_dates

    # Delete the booking
    booking.delete()

    # Create notification for the other user
    Notification.objects.create(
        user=recipient,
        message=f"{request.user.username} cancelled your "
                f"confirmed vacation exchange for {cancelled_dates}.",
        link=reverse('view_profile', args=[request.user.id])
    )

    # Send email to the other user (optional but useful)
    send_mail(
        subject='Vacation exchange cancelled',
        message=(
            f"{request.user.username} has cancelled the "
            f"confirmed vacation exchange.\n\n"
            f"Dates: {cancelled_dates}\n\n"
            "Log in to TravelSwap to view their profile or make a new request."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient.email],
        fail_silently=False,
    )

    # Feedback for the user performing the cancellation
    messages.success(request, "Vacation exchange cancelled and user notified.")
    return redirect('view_profile', user_id=profile_user.id)


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


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
