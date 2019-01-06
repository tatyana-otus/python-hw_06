import pytz
from datetime import datetime

from django.utils import timezone
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from hasker.qa.models import Question, Tag, Answer
from hasker.users.models import Profile
from .helper import *


class ViewTest(TestCase):

    def test_question_404(self):
        client = Client()
        response = client.get(reverse('qa:detail', args=[1234]))
        self.assertEqual(response.status_code, 404)

    def test_tag_404(self):
        client = Client()
        response = client.get(reverse('qa:tag', args=[1234]))
        self.assertEqual(response.status_code, 404)

    def test_question(self):
        client = Client(enforce_csrf_checks=True)
        create_user_and_login(client)
        title = 'Why ?'
        response, _ = create_question(client, title, 'why ...', 't1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, title)

        q = Question.objects.get(title=title)
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertEqual(response.status_code, 200)

    def test_tag(self):
        client = Client(enforce_csrf_checks=True)
        create_user_and_login(client)
        tag = 't1'
        response, _ = create_question(client, 'Why ?', 'why ...', tag)

        t = Tag.objects.get(name=tag)
        response = client.get(reverse('qa:tag', args=[t.id]))
        self.assertEqual(response.status_code, 200)

    def test_accept(self):
        q_user_acc = {'username': 'tany_1',
                      'email': 'email@mail.com',
                      'password': '12345_qwert'
                      }
        a_user_acc = {'username': 'tany_2',
                      'email': 'email2@mail.com',
                      'password': '12345_qwert'
                      }
        q_user = Profile.objects.create_user(**q_user_acc)
        a_user = Profile.objects.create_user(**a_user_acc)

        q = Question.objects.create(author=q_user,
                                    title='Some title',
                                    body='some body ...',
                                    date=datetime.now(pytz.timezone(settings.TIME_ZONE)))
        a = Answer.objects.create(author=a_user,
                                  body='some answer ...',
                                  date=datetime.now(pytz.timezone(settings.TIME_ZONE)),
                                  question=q)
        q.answers.add(a)

        client = Client()
        client.login(username=q_user_acc['username'],
                     password=q_user_acc['password'])
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('qa:accept'))

        client = Client()
        client.login(username=a_user_acc['username'],
                     password=a_user_acc['password'])
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('qa:accept'))
