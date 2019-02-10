import logging
from rest_framework import generics
from rest_framework import pagination
from rest_framework.permissions import IsAuthenticated

from django.db.models import Count, F, Q
from django.conf import settings
from django.shortcuts import get_object_or_404

from hasker.qa.models import Question
from hasker.qa.utils.helper import *
from .serializers import QuestionSerializer, AnswerSerializer


class SetPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page'
    max_page_size = 100


class IndexQuestionsView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    pagination_class = SetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        search_string = self.request.GET.get('find', "")
        tag_names, find_value = parse_search_string(search_string)

        qs = Question.objects\
                     .prefetch_related('tags')\
                     .select_related('author')\
                     .annotate(Count('answers', distinct=True),
                               Count('u_likes', distinct=True),
                               Count('u_dislikes', distinct=True))\
                     .annotate(votes=F('u_likes__count') - F('u_dislikes__count'))
        if find_value:
            qs = qs.filter(Q(title__contains=find_value) |
                           Q(body__contains=find_value))
        qs = set_filter_by_tag_names(qs, tag_names)
        return qs.order_by('-date', '-votes')


class QuestionView(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        question_pk = self.kwargs.get('pk')
        return Question.objects.filter(pk=question_pk)\
                               .annotate(Count('u_likes', distinct=True),
                                         Count('u_dislikes', distinct=True))\
                               .annotate(votes=F('u_likes__count') -
                                         F('u_dislikes__count'))


class TrendingQuestionsView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Question.objects.order_by('-votes', '-date')\
                               .annotate(Count('u_likes', distinct=True),
                                         Count('u_dislikes', distinct=True))\
                               .annotate(votes=F('u_likes__count') -
                                         F('u_dislikes__count'))[:settings.TRENDING_NUM]


class AnswersView(generics.ListAPIView):
    serializer_class = AnswerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        question_pk = self.kwargs.get('pk')
        q = get_object_or_404(Question, pk=question_pk)
        return q.answers.all()\
                .annotate(Count('u_likes', distinct=True),
                          Count('u_dislikes', distinct=True))\
                .annotate(votes=F('u_likes__count') -
                          F('u_dislikes__count'))\
                .order_by('-date')\
                .select_related('author')
