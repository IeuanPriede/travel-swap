from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import CustomUserCreationForm


# Create your views here.
@login_required
def my_profiles(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profiles/index.html', {'profile': profile})


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