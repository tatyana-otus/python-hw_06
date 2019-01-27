from string import Template

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm
from django.forms import FileInput

from .models import Profile


class ProfileCreationForm(UserCreationForm):
    header_title = "SignUp"
    submit_title = "SignUp"
    field_order = ['username', 'email', 'password1', 'password2', 'avatar']

    class Meta:
        model = Profile
        fields = ['avatar', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LoginForm(AuthenticationForm):
    header_title = "Login"
    submit_title = "Login"
    field_order = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(AuthenticationForm):
        model = Profile
        fields = ('username', 'password')


class ProfileChangeForm(ModelForm):
    header_title = "Settings"
    submit_title = "Save"
    field_order = ['username', 'email', 'avatar']

    class Meta:
        model = Profile
        fields = ['username', 'email', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].disabled = True
        self.fields['username'].help_text = ""
