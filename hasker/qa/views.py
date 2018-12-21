#from django.shortcuts import render

from django.http import HttpResponse
from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Count


from .models import Question
from .forms import QChangeForm


class IndexView(generic.ListView):
    template_name = 'home.html'  
    context_object_name = 'question_list' 
    paginate_by = 4

    def get_queryset(self):
        return Question.objects\
               .order_by('-date')\
               .prefetch_related('tags')\
               .select_related('author')\
               .annotate(Count('u_likes'), Count('u_dislikes'))\
               .annotate(Count('answers'))


class AddQuestionView(generic.View):
    template_name='users/signup.html', 
    form_class = QChangeForm
    ctx_obj_name = 'form'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {self.ctx_obj_name: self.form_class})
  
    def post(self, request, *args, **kwargs):    
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            q = form.save()
            return redirect(reverse('qa:questions'))
        return render(request, self.template_name, {self.ctx_obj_name: form})  


class TrendingView(generic.ListView):
    template_name = 'qa/trending.html'  
    context_object_name = 'question_list'

    def get_queryset(self):
        return Question.objects.order_by('-date')\
                       .annotate(Count('u_likes'),
                                 Count('u_dislikes'))[:3] # !!!


class QuestionDetailView(generic.DetailView):
    pass   

class QuestionsByTagView(generic.DetailView):
    pass    
