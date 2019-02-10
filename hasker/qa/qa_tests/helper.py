from faker import Factory
import pytz
from datetime import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from hasker.users.models import Profile
from hasker.qa.models import Question, Answer

default_password = '12345_qwert'
default_account = {'username': 'tany_1',
                   'email': 'email@mail.com',
                   'password': default_password
                   }
faker = Factory.create()


def create_user_and_login(client, account=default_account):
    user = Profile.objects.create_user(**account)
    response = client.get(reverse('users:login'))
    post_data = {'csrfmiddlewaretoken': response.context['csrf_token'],
                 'username': account['username'],
                 'password': account['password']
                 }
    response = client.post(reverse('users:login'), post_data, follow=True)
    return response, client


def create_question_by_http(client, title, body, tags):
    response = client.get(reverse('qa:ask'), follow=True)
    post_data = {'csrfmiddlewaretoken': response.context['csrf_token'],
                 'title': title,
                 'body': body,
                 'form_tags': tags
                 }
    response = client.post(reverse('qa:ask'), post_data, follow=True)
    return response, client


def create_user():
    acc = {'username': faker.user_name(),
           'email': faker.email(),
           'password': default_password
           }
    return Profile.objects.create_user(**acc)


def create_question(author=None):
    if author is None:
        author = create_user()
    return Question.objects.create(author=author,
                                   title=faker.text()[:20],
                                   body=faker.text()[:100],
                                   date=datetime.now(pytz.timezone(settings.TIME_ZONE)))


def create_answer(question, author=None):
    if author is None:
        author = create_user()
    a = Answer.objects.create(author=author,
                              body=faker.text()[:100],
                              date=datetime.now(pytz.timezone(settings.TIME_ZONE)),
                              question=question)
    question.answers.add(a)
    return a
