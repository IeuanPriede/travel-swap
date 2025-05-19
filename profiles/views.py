from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile, HouseImage, MatchResponse
from .forms import (
    CustomUserCreationForm,
    ProfileForm,
    UserForm,
    ImageFormSet,
    SearchForm,
)
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from cloudinary.uploader import destroy
from django.template.loader import render_to_string
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.views.decorators.http import require_POST


# Create your views here.
# View to display the logged-in user's profile
@login_required
def profile_view(request):
    # Get or create a Profile instance tied to the logged-in user
    profile, created = Profile.objects.get_or_create(user=request.user)
    house_images = profile.house_images.all()
    # Pass profile object to the template
    return render(request, 'profiles/profile.html', {
        'profile': profile,
        'house_images': house_images
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
        formset = ImageFormSet(queryset=HouseImage.objects.filter(
            profile=profile
                ))

        # Check all forms individually first
        user_form_valid = user_form.is_valid()
        profile_form_valid = profile_form.is_valid()
        print("DEBUG - Form valid states:",
              user_form_valid, profile_form_valid)
        formset_valid = formset.is_valid()

        # Debug: print validation states
        print("UserForm valid:", user_form_valid)
        print("ProfileForm valid:", profile_form_valid)
        print("Formset valid:", formset_valid)
        print("UserForm errors:", user_form.errors)
        print("ProfileForm errors:", profile_form.errors)
        print("Formset errors:", formset.errors)

        if user_form.is_valid() and profile_form.is_valid():
            print("All forms valid")
            user_form.save()
            profile_form.save()
            images = formset.save(commit=False)
            for image in images:
                if image.image:  # only save if image was uploaded
                    image.profile = profile
                    image.save()

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
@require_POST
def set_main_image(request, image_id):
    image = get_object_or_404(
        HouseImage, id=image_id, profile__user=request.user)

    # Clear previous main image
    HouseImage.objects.filter(profile=image.profile).update(is_main=False)

    # Set new main image
    image.is_main = True
    image.save()

    return redirect('edit_profile')


@login_required
def upload_images(request):
    profile = get_object_or_404(Profile, user=request.user)
    existing_images = HouseImage.objects.filter(profile=profile)

    if request.method == 'POST':
        formset = ImageFormSet(request.POST, request.FILES,
                               queryset=existing_images)

        # Mark empty forms as permitted
        for form in formset.forms:
            if not form.has_changed():
                form.empty_permitted = True

        for form in formset.forms:
            if not form.has_changed():
                form.empty_permitted = True

        if formset.is_valid():
            instances = formset.save(commit=False)
            if formset.is_valid():
                instances = formset.save(commit=False)
            new_images = []

            for instance in instances:
                instance.profile = profile
                new_images.append(instance)

            # Save new images and auto-set first as main if none exists
            for i, image in enumerate(new_images):
                if (
                    not profile.house_images.filter(is_main=True).exists()
                    and i == 0
                ):
                    image.is_main = True
                image.save()

            # Handle manual main image selection (if applicable)
            selected_main_id = request.POST.get('main_image')
            if selected_main_id:
                for image in profile.house_images.all():
                    image.is_main = (str(image.id) == selected_main_id)
                    image.save()

            messages.success(request, "Images updated successfully.")
        else:
            messages.error(request, "There was a problem updating images.")

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
    image = get_object_or_404(HouseImage, id=image_id)

    # Ensure the image belongs to the logged-in user
    if image.profile.user != request.user:
        return JsonResponse({"error": "Forbidden"}, status=403)

    if request.method == "POST":
        # Extract the public ID from the image URL
        public_id = image.image.name.rsplit(
            '.', 1)[0]  # Removes file extension
        try:
            destroy(public_id)  # Cloudinary file delete
        except Exception as e:
            print(f"Error deleting image from Cloudinary: {e}")

        image.delete()  # Delete the DB entry
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def home(request):
    # Get the IDs of profiles the user already responded to
    responded_ids = MatchResponse.objects.filter(
        from_user=request.user
    ).values_list('to_profile_id', flat=True)

# Start with visible, unrated profiles not belonging to the user
    profiles = Profile.objects.filter(
        ~Q(user=request.user),
        is_visible=True
    ).exclude(id__in=responded_ids)

    form = SearchForm(request.GET or None)

    if form.is_valid():
        for field, value in form.cleaned_data.items():
            if value:
                profiles = profiles.filter(**{field: True})

    # Get the first profile from the filtered list
    next_profile = profiles.first()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/profile_card.html', {
            'profile': next_profile
        }, request=request)
        return JsonResponse({'next_profile_html': html})

    return render(request, 'home.html', {
        'profile': next_profile,
        'form': form  # pass form to template
    })


@csrf_exempt
@login_required
def next_profile(request):
    if request.method == 'POST':
        # Just skip saving anything, move to next profile
        data = json.loads(request.body)
        profile_id = data.get('profile_id')
        profile = get_object_or_404(Profile, id=profile_id)

        # Simulate skipping by marking it "viewed" (optional enhancement)
        request.session.setdefault('skipped_profiles', []).append(profile.id)

        responded_ids = MatchResponse.objects.filter(
            from_user=request.user).values_list('to_profile_id', flat=True)
        skipped_ids = request.session.get('skipped_profiles', [])

        next_profile = Profile.objects.filter(
            ~Q(user=request.user),
            is_visible=True
        ).exclude(id__in=responded_ids).exclude(id__in=skipped_ids).first()

        html = render_to_string('partials/profile_card.html', {
            'profile': next_profile}, request=request)

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
        liked=True
    ).select_related('to_profile', 'to_profile__user')

    return render(request, 'travel_log.html', {
        'liked_profiles': liked_profiles
    })


@login_required
def view_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, is_visible=True)

    return render(request, 'profiles/view_profile.html', {
        'profile': profile
    })


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')
