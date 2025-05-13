from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import Profile, HouseImage


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio',
            'location',
            'house_description',
            'is_visible',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'house_description': forms.Textarea(attrs={'rows': 4}),
        }


class ImageForm(forms.ModelForm):
    image = forms.ImageField(required=False)  # ← make the image field optional

    class Meta:
        model = HouseImage
        fields = ['image']


ImageFormSet = modelformset_factory(
    HouseImage,
    form=ImageForm,
    extra=3,
    max_num=5,
    validate_max=True,
    can_delete=True
)
