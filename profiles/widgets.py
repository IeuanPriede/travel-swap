from django_countries.fields import CountryField
from django import forms


class CountrySelectWidgetNoFlags(forms.Select):
    """
    Completely custom CountrySelectWidget that avoids any flag or JS injection.
    """
    def __init__(self, attrs=None):
        choices = list(CountryField().get_choices())
        super().__init__(attrs, choices=choices)
