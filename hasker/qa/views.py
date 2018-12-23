from django.http import HttpResponse
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from django.db.models import F
from django import forms

from .models import Question
from .forms import QChangeForm, AddAnswerForm

TRENDING_NUM = 20
QUESTION_PAGINATE = 4
ANSWER_PAGINATE = 2

class IndexView(generic.ListView):
    template_name = 'home.html'  
    context_object_name = 'question_list' 
    paginate_by = QUESTION_PAGINATE
    sort = {'new': '-date', 'hot': 'votes'}
    default_sort = 'new'

    def get_queryset(self):
        value = self.request.GET.get('tab', self.default_sort)
        return  Question.objects\
                        .prefetch_related('tags')\
                        .select_related('author')\
                        .annotate(Count('u_likes'), Count('u_dislikes'))\
                        .annotate(Count('answers'))\
                        .annotate(votes=F('u_likes__count')-F('u_dislikes__count'))\
                        .order_by(self.sort[value])


class AddQuestionView(generic.View):
    template_name='users/signup.html', 
    form_class = QChangeForm
    ctx_obj_name = 'form'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {self.ctx_obj_name: self.form_class})
  
    def post(self, request, *args, **kwargs):    
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('qa:questions'))
        return render(request, self.template_name, {self.ctx_obj_name: form})  


class TrendingView(generic.ListView):
    template_name = 'qa/trending.html'  
    context_object_name = 'question_list'

    def get_queryset(self):
        return Question.objects.order_by('-date')\
                       .annotate(Count('u_likes'), Count('u_dislikes'))\
                       .annotate(votes=F('u_likes__count')-F('u_dislikes__count'))[:TRENDING_NUM] 


class QuestionDetailView(generic.View):
    template_name = 'qa/question_detail.html'

    def get(self, request, *args, **kwargs):
        form = AddAnswerForm()
        queryset = Question.objects\
                           .annotate(Count('u_likes'), Count('u_dislikes'))\
                           .annotate(votes=F('u_likes__count')-F('u_dislikes__count'))
        question = get_object_or_404(queryset, pk=kwargs['pk'])
        return render(request, self.template_name, {'question': question, 'form': form})
  
    def post(self, request, *args, **kwargs): 
        if not request.user.is_authenticated:
            return redirect(reverse('user:login'))
        question_pk = kwargs.get('pk') 
        form = AddAnswerForm(request.POST)
        if form.is_valid():
            form.save(request.user, question_pk)
            return redirect(reverse('qa:detail', args=[question_pk]))
        question = get_object_or_404(Question, pk=question_pk)  # !!!!  
        return render(request, self.template_name,  {'question': question, 'form': form})


class AnswerView(generic.ListView):
    template_name = 'qa/answers_list.html'
    context_object_name = 'items' 
    paginate_by = ANSWER_PAGINATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_pk = self.kwargs.get('pk')
        context['question'] = Question.objects.get(pk=question_pk)
        return context

    def get_queryset(self):
        question_pk = self.kwargs.get('pk')
        q = Question.objects.get(pk=question_pk)
        return q.answers.all()\
                .annotate(Count('u_likes'), Count('u_dislikes'))\
                .annotate(votes=F('u_likes__count')-F('u_dislikes__count'))\
                .order_by('-date')\
                .select_related('author')


class QuestionsByTagView(generic.ListView):
    pass    
