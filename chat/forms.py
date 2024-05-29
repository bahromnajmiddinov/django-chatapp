from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList

from .models import Chat


class PublicGroupForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['name', 'username', 'avatar']


class PrivateGroupForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['name', 'avatar']
