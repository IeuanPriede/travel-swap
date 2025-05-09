from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import CustomUserCreationForm
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