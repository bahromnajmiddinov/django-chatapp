from django import forms
from django.core.exceptions import ValidationError

from .models import Account


class AccountEditForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'description', 'avatar']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        allowed = ['1', '2', '3', '4', '5', '7', '8', '9', '0']
        for number in str(phone_number):
            if number not in allowed:
                raise ValidationError('Only numbers are allowed')

        return phone_number
    