from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from .forms import ProfileChangeForm


class EditProfile(View):
    context_object_name = 'form'
    form_class = ProfileChangeForm
    template_name = 'users/signup.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,
                      {self.context_object_name:
                       self.form_class(instance=request.user)})

    def post(self, request, *args, **kwargs):
        bound_form = self.form_class(request.POST,
                                     request.FILES,
                                     instance=request.user)
        if bound_form.is_valid():
            bound_form.save()
            return redirect('users:settings')
        return render(request, self.template_name,
                      {self.context_object_name: bound_form})
