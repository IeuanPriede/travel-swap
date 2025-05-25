from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import Profile, HouseImage
from django.core.exceptions import ValidationError
from PIL import Image


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'first_name': forms.TextInput
            (attrs={'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(
                attrs={'autocomplete': 'family-name'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio',
            'location',
            'house_description',
            'available_dates',
            'is_visible',
            'pets_allowed',
            'has_pool',
            'more_than_3_bedrooms',
            'near_beach',
            'in_mountains',
            'in_city',
            'in_rural',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'house_description': forms.Textarea(attrs={'rows': 4}),
            'pets_allowed': forms.CheckboxInput(),
            'has_pool': forms.CheckboxInput(),
            'more_than_3_bedrooms': forms.CheckboxInput(),
            'near_beach': forms.CheckboxInput(),
            'in_mountains': forms.CheckboxInput(),
            'in_city': forms.CheckboxInput(),
            'in_rural': forms.CheckboxInput(),
            'available_dates': forms.TextInput(attrs={
                    'class': 'form-control',
                    'id': 'available-dates',
                    'placeholder': 'Select an availability range',
                    'autocomplete': 'off',
                }),
        }


class SearchForm(forms.Form):
    pets_allowed = forms.BooleanField(required=False)
    has_pool = forms.BooleanField(required=False)
    more_than_3_bedrooms = forms.BooleanField(required=False)
    near_beach = forms.BooleanField(required=False)
    in_mountains = forms.BooleanField(required=False)
    in_city = forms.BooleanField(required=False)
    in_rural = forms.BooleanField(required=False)


class ImageForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png'
        })
    )

    class Meta:
        model = HouseImage
        fields = ['image']

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            print("No image provided")
            return None

        if image.size > 2 * 1024 * 1024:
            raise ValidationError('Image size must be under 2MB.')

        try:
            img = Image.open(image)
            print("Image format detected:", img.format)
            if img.format not in ['JPEG', 'PNG']:
                raise ValidationError('Only JPEG and PNG images are allowed.')

            image.seek(0)  # ✅ Reset file pointer for Cloudinary

        except Exception as e:
            print("Image validation error:", e)
            raise ValidationError('Invalid image file.')

        return image


ImageFormSet = modelformset_factory(
    HouseImage,
    form=ImageForm,
    extra=5,
    max_num=5,
    validate_max=True,
)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=150, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
