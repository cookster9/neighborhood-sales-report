from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
    your_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

class NeighborhoodUpdateForm(forms.Form):
    id = forms.IntegerField(required=True, help_text="Enter a neighborhood ID to update its properties")


    def clean_id(self):
        data = self.cleaned_data['id']

        # Check if a date is not in the past.
        if data < 1:
            raise ValidationError(_('Invalid ID - must be greater than 0'))
        return data