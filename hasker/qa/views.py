from django.http import HttpResponse
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from django.db.models import F
from django import forms
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from .models import Question, Answer
from .forms import QChangeForm, AddAnswerForm

TRENDING_NUM = 20
QUESTION_PAGINATE = 4
ANSWER_PAGINATE = 2

class IndexView(generic.ListView): # GET param 'tab' + 'page' !!!
    template_name = 'home.html'
    context_object_name = 'question_list'
    paginate_by = QUESTION_PAGINATE
    sort = {'new': ['-date', '-votes'], 'hot': ['-votes', '-date']}
    default_sort = 'new'


    def set_sort(self, queryset):
        value = self.request.GET.get('tab', self.default_sort)
        return queryset.order_by(*self.sort[value])

    def set_filter(self, queryset):
        return queryset


    def get_queryset(self):
        value = self.request.GET.get('tab', self.default_sort)
        return  Question.objects\
                        .prefetch_related('tags')\
                        .select_related('author')\
                        .annotate(Count('answers', distinct=True),\
                                  Count('u_likes', distinct=True),\
                                  Count('u_dislikes', distinct=True))\
                        .annotate(votes=F('u_likes__count') - F('u_dislikes__count'))\
                        .order_by(*self.sort[value])


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
        return Question.objects.order_by('-votes', '-date')\
                       .annotate(Count('u_likes', distinct=True),
                                 Count('u_dislikes', distinct=True))\
                       .annotate(votes=F('u_likes__count') -\
                                       F('u_dislikes__count'))[:TRENDING_NUM]


class QA_DetailView(generic.ListView):
    template_name = 'qa/qa_detail.html'
    context_object_name = 'items'
    paginate_by = ANSWER_PAGINATE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.answer_form = AddAnswerForm()


    def get_queryset(self):
        question_pk = self.kwargs.get('pk')
        q = Question.objects.get(pk=question_pk)
        return q.answers.all()\
                .annotate(Count('u_likes', distinct=True),\
                          Count('u_dislikes', distinct=True))\
                .annotate(votes=F('u_likes__count') -\
                                F('u_dislikes__count'))\
                .order_by('-date')\
                .select_related('author')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_pk = self.kwargs.get('pk')

        context['question'] = Question.objects\
                                      .annotate(Count('u_likes', distinct=True),
                                                 Count('u_dislikes', distinct=True))\
                                      .annotate(votes=F('u_likes__count') -\
                                                       F('u_dislikes__count'))\
                                      .get(pk=question_pk)
        context['form'] = self.answer_form
        return context


    def get(self, request, *args, **kwargs):
        self.answer_form = AddAnswerForm()
        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('user:login'))
        question_pk = kwargs.get('pk')
        form = AddAnswerForm(request.POST)
        if form.is_valid():
            form.save(request.user, question_pk)
            return redirect(reverse('qa:detail', args=[question_pk]))
        return super().get(request, *args, **kwargs)


@require_http_methods(["POST"])
def update_votes(request):
    item_id = request.POST.get('id')
    item_value = request.POST.get('value')
    item_type = request.POST.get('type')
    try:
        if item_type == 'question':
            obj = Question.objects.get(pk=item_id)
        elif item_type == 'answer':
            obj = Answer.objects.get(pk=item_id)
        else:
            raise ValueError("Wrong update")
        if item_value == "hate":
            obj.hate_this(request.user)
        elif item_value == "love":
            obj.hate_this(request.user, False)
    except Exception as e:
        return JsonResponse({'status': 'FAIL'})
    return JsonResponse({'status': 'OK'})


class QuestionsByTagView(generic.ListView):
    pass
