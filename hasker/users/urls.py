from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required

from . import views
from . import forms

app_name = "users"
urlpatterns = [
    path('signup/', generic.CreateView.as_view(form_class=forms.ProfileCreationForm,
                                               success_url=reverse_lazy('users:login'),
                                               template_name='users/signup.html'),
         name='signup'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/signup.html',
                                     form_class=forms.LoginForm,
                                     success_url=reverse_lazy('qa:questions')),
        name='login'),
    path(
        'settings/', login_required(views.EditProfile.as_view(), login_url='users:login'), name='settings'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(), name='logout'),
]
