from datetime import datetime
import pytz

from django.db import models
from django.conf import settings
from django.urls import reverse

class QA(models.Model):
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)
    date = models.DateTimeField()
    title = None

    class Meta:
        abstract = True

    def get_tags(self):
        return None

    def show_likes(self):
        return str(self.u_likes.count())

    def show_dislikes(self):
        return str(self.u_dislikes.count())

    def hate_this(self, user, hate = True):
        if hate:
            if user not in self.u_dislikes.all():
                self.u_dislikes.add(user)
                self.u_likes.remove(user)
            else:
                raise ValueError("Already voted")
        else:
            if user not in self.u_likes.all():
                self.u_likes.add(user)
                self.u_dislikes.remove(user)
            else:
                raise ValueError("Already voted")


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def get_absolute_url(self):
        return reverse('qa:tag', args=[self.id])


class Answer(QA):
    u_likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     related_name='answer_likes_set',
                                     blank=True)
    u_dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='answer_dislikes_set',
                                        blank=True)
    right = models.BooleanField(default=False)


    def save_new_answer(self, author, question_pk, body):
        self.date = datetime.now();
        self.author = author
        self.save()
        q = Question.objects.get(pk=question_pk)
        q.answers.add(self)


class Question(QA):
    TAGS_NUM = 3

    title = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, blank=True)
    answers = models.ManyToManyField(Answer, blank=True)
    u_likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     related_name='question_likes_set',
                                     blank=True)
    u_dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='question_dislikes_set',
                                        blank=True)

    def show_tags(self):
        return " ".join(t.name for t in self.tags.all())

    def get_tags(self):
        return self.tags.all()

    def get_absolute_url(self):
        return reverse('qa:detail', args=[self.id])

    def get_absolute_answers_url(self):
        return reverse('qa:answers', args=[self.id])

    def hours_ago(self):
        delta = datetime.now(pytz.timezone(settings.TIME_ZONE)) - self.date
        return str(delta.total_seconds() // 3600)

    def save_new_question(self, author, tag_list):
        self.date = datetime.now();
        self.author = author
        self.save()
        for t in tag_list:
            tag, created = Tag.objects.get_or_create(name=t)
            if created:
                tag.save()
            self.tags.add(tag)
