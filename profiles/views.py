from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile, HouseImage
from .forms import (
    CustomUserCreationForm,
    ProfileForm,
    UserForm,
    ImageFormSet,
)
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse


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
def upload_images(request):
    profile = get_object_or_404(Profile, user=request.user)
    existing_images = HouseImage.objects.filter(profile=profile)

    if request.method == 'POST':
        formset = ImageFormSet(request.POST, request.FILES,
                               queryset=existing_images)

        for form in formset.forms:
            if not form.instance.pk:
                form.empty_permitted = True

            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.profile = profile
                    instance.save()

            print("Remaining images:", HouseImage.objects.filter(
                profile=profile))

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
        if image.image:
            image.image.delete(save=False)  # Delete the file from media
        image.delete()  # Delete the model instance
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"}, status=400)


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')
