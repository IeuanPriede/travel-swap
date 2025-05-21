from django import forms
from .models import Message, BookingRequest


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Write your message...'}),
        }


class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['requested_dates']
        widgets = {
            'requested_dates': forms.TextInput(attrs={
                'name': 'requested_dates',
                'class': 'form-control',
                'id': 'requested-dates',
                'placeholder': 'Select exchange dates'
            }),
        }
