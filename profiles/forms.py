from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import Profile, HouseImage
from django.core.exceptions import ValidationError
from PIL import Image
from .widgets import CountrySelectWidgetNoFlags
from django_countries.fields import CountryField


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError(
                "Username cannot be blank or spaces only.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError(
                "Email cannot be blank or spaces only.")
        return email


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

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Username cannot be blank.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("Email cannot be blank.")
        return email

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '').strip()
        return name  # Optional: add validation if required

    def clean_last_name(self):
        name = self.cleaned_data.get('last_name', '').strip()
        return name


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
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'style': 'width: 100%; max-width: 100%;'
            }),
            'house_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'style': 'width: 100%; max-width: 100%;'
            }),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].widget = CountrySelectWidgetNoFlags(
            attrs={'class': 'form-control select2'}
        )

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '').strip()
        if not bio:
            raise forms.ValidationError("Bio cannot be blank.")
        return bio

    def clean_house_description(self):
        desc = self.cleaned_data.get('house_description', '').strip()
        if not desc:
            raise forms.ValidationError("House description cannot be blank.")
        return desc

    def clean_available_dates(self):
        dates = self.cleaned_data.get('available_dates', '').strip()
        return dates


class SearchForm(forms.Form):
    location = CountryField(
        blank_label='(select country)').formfield(required=False)
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
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    subject = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 5
    }))

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Name cannot be blank.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("Email cannot be blank.")
        return email

    def clean_subject(self):
        subject = self.cleaned_data.get('subject', '').strip()
        if not subject:
            raise forms.ValidationError("Subject cannot be blank.")
        return subject

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise forms.ValidationError("Message cannot be blank.")
        return message
