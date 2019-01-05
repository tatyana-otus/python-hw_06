from django import forms
from django.http import HttpResponse
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, F, Q
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from hasker.qa.utils.helper import *
from .models import Question, Answer, Tag
from .forms import AddQuestionForm, AddAnswerForm

TRENDING_NUM = 20
QUESTION_PAGINATE = 4
ANSWER_PAGINATE = 2


class IndexView(generic.ListView):
    template_name = 'home.html'
    paginate_by = QUESTION_PAGINATE
    context_object_name = 'question_list'
    sort = {'new': ['-date', '-votes'], 'hot': ['-votes', '-date']}
    default_sort = 'new'
    search_string = ""
    title = ""

    def set_sort(self, queryset):
        value = self.request.GET.get('tab', self.default_sort)
        return queryset.order_by(*self.sort[value])

    def set_filter(self, queryset):
        return queryset

    def build_queryset(self):
        return  Question.objects\
                        .prefetch_related('tags')\
                        .select_related('author')\
                        .annotate(Count('answers', distinct=True),\
                                  Count('u_likes', distinct=True),\
                                  Count('u_dislikes', distinct=True))\
                        .annotate(votes=F('u_likes__count') - F('u_dislikes__count'))

    def get_queryset(self):
        qs = self.build_queryset()
        qs = self.set_filter(qs)
        qs = self.set_sort(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_string'] = self.search_string
        context['title'] = self.title
        return context


class SearchView(IndexView):
    default_sort = 'hot'
    title = "Search result"

    def set_filter(self, queryset):
        search_string = self.request.GET.get('find', "")
        tag_names, find_value = parse_search_string(search_string)
        self.search_string = search_string
        if find_value:
            queryset = queryset.filter(Q(title__contains=find_value) |
                                       Q(body__contains=find_value))
        queryset = set_filter_by_tag_names(queryset, tag_names)
        return queryset


class TaggedView(IndexView):
    default_sort = 'hot'
    title = "Tag result"

    def set_filter(self, queryset):
        tag_pk = self.kwargs.get('pk')
        tag = get_object_or_404(Tag, pk=tag_pk)
        self.search_string = "tag:{}".format(tag.name)
        queryset = queryset.filter(tags__id=tag_pk)
        return queryset


class AddQuestionView(generic.View):
    template_name='users/signup.html',
    form_class = AddQuestionForm
    ctx_obj_name = 'form'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {self.ctx_obj_name: self.form_class})
  
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(request.user)
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
    form_class = AddAnswerForm
    context_object_name = 'items'
    paginate_by = ANSWER_PAGINATE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.answer_form = self.form_class()


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
        self.answer_form = self.form_class()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('user:login'))
        question_pk = kwargs.get('pk')
        form = self.form_class(request.POST)
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
    votes = obj.u_likes.count() - obj.u_dislikes.count();
    return JsonResponse({'status': 'OK', 'votes': votes})


@require_http_methods(["POST"])
def accept_answer(request):
    item_id = request.POST.get('id')
    item_value = request.POST.get('value')
    try:
        obj = Answer.objects.get(pk=item_id)
        result = obj.accept(request.user)
    except Exception as e:
        return JsonResponse({'status': 'FAIL'})
    return JsonResponse({'status': 'OK', "accepted": result})
