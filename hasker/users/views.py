#from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth import views
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import ProfileCreationForm, ProfileChangeForm


def EditProfile(request):
    if not request.user.is_authenticated:
        return redirect(reverse('users:login'))

    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('users:settings'))
        else:
            return render(request, 'users/signup.html', {'form': form})     
    else:
        form = ProfileChangeForm(instance=request.user)
        args = {'form': form}
        return render(request, 'users/signup.html', args)
