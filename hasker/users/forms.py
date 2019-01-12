from string import Template

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm
from django.forms import FileInput

from .models import Profile


class ProfileCreationForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'username', 'email']

    header_title = "SignUp"
    submit_title = "SignUp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Login"
        self.fields['email'].label = "Emai"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Repeat Password"
        self.fields['avatar'].label = "Avatar"

    field_order = ['username', 'email', 'password1', 'password2', 'avatar']


class LoginForm(AuthenticationForm):
    header_title = "Login"
    submit_title = "Login"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Login"
        self.fields['password'].label = "Password"

    class Meta(AuthenticationForm):
        model = Profile
        fields = ('username', 'password')

    field_order = ['username', 'password']


class ProfileChangeForm(ModelForm):
    header_title = "Settings"
    submit_title = "Save"

    class Meta:
        model = Profile
        fields = ['username', 'email', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Login"
        self.fields['email'].label = "Emai"
        self.fields['avatar'].label = "Avatar"
        self.fields['username'].disabled = True
        self.fields['username'].help_text = ""

    field_order = ['username', 'email', 'avatar']
