from datetime import datetime
import pytz

from django.utils import timezone
from django.db import models, transaction
from django.conf import settings
from django.urls import reverse

from hasker.qa.utils.helper import *


class QA(models.Model):
    body = models.TextField(verbose_name='Text')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)
    date = models.DateTimeField()
    title = None

    class Meta:
        abstract = True

    def get_tags(self):
        return None

    def counts_likes(self):
        return str(self.u_likes.count())

    def counts_dislikes(self):
        return str(self.u_dislikes.count())

    def hate_this(self, user, hate=True):
        with transaction.atomic():
            if hate:
                self.u_likes.remove(user)
                change_hate = self.u_dislikes
            else:
                self.u_dislikes.remove(user)
                change_hate = self.u_likes
            if change_hate.filter(pk=user.id).exists():
                change_hate.remove(user)
            else:
                change_hate.add(user)
        return self.u_likes.count() - self.u_dislikes.count()


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)


class Answer(QA):
    u_likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     related_name='answer_likes_set',
                                     blank=True)
    u_dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='answer_dislikes_set',
                                        blank=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    def save_new_answer(self, author, question_pk, body):
        with transaction.atomic():
            q = Question.objects.get(pk=question_pk)
            self.date = datetime.now(pytz.timezone(settings.TIME_ZONE))
            self.author = author
            self.question = q
            self.save()
            q.answers.add(self)
            new_answer_notify(q.author.email, reverse('qa:detail', args=[question_pk]))

    def accept(self, question_author):
        with transaction.atomic():
            q = self.question
            if q.author != question_author or self not in q.answers.all():
                raise ValueError("Invalid value")
            if q.accepted_answer == self:
                q.accepted_answer = None
                q.save()
                return
            q.accepted_answer = self
            q.save()
            return True


class Question(QA):
    TAGS_NUM = 3

    title = models.CharField(max_length=255, verbose_name='Title')
    tags = models.ManyToManyField(Tag, blank=True)
    accepted_answer = models.ForeignKey(Answer, on_delete=models.CASCADE,
                                        related_name='accepted_answer',
                                        blank=True, null=True)
    answers = models.ManyToManyField(Answer, related_name='question_answers_set',
                                     blank=True)
    u_likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     related_name='question_likes_set',
                                     blank=True)
    u_dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='question_dislikes_set',
                                        blank=True)

    def show_tags(self):
        return list(self.tags.values_list('name', flat=True))

    def get_tags(self):
        return self.tags.all()

    def save_new_question(self, author, tag_list):
        with transaction.atomic():
            self.date = datetime.now(pytz.timezone(settings.TIME_ZONE))
            self.author = author
            self.save()
            for t in tag_list:
                self.tags.add(Tag.objects.get_or_create(name=t)[0])
