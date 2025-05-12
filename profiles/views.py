from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import CustomUserCreationForm, ProfileForm, UserForm
from django.contrib.auth import login, logout
from django.contrib import messages


# Create your views here.
# View to display the logged-in user's profile
@login_required
def profile_view(request):
    # Get or create a Profile instance tied to the logged-in user
    profile, created = Profile.objects.get_or_create(user=request.user)
    # Pass profile object to the template
    return render(request, 'profiles/profile.html', {'profile': profile})


# Edit profile view
@login_required
def edit_profile(request):
    # Get the current user's profile
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        # Handle the form submission
        user_form = UserForm(
            request.POST, instance=request.user
            )  # for updating the user model
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=profile
            )  # for updating the profile model

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
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

    return render(request, 'profiles/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


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


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')