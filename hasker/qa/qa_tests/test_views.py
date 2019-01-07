import pytz
from datetime import datetime

from django.utils import timezone
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from hasker.qa.models import Question, Tag, Answer
from hasker.qa.views import IndexView
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
        response, client = create_question_by_http(client, title, 'why ...', 't1')
        self.assertContains(response, title, status_code=200)

        q = Question.objects.get(title=title)
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertEqual(response.status_code, 200)

    def test_tag(self):
        client = Client(enforce_csrf_checks=True)
        create_user_and_login(client)
        tag = 't1'
        response, client = create_question_by_http(client, 'Why ?', 'why ...', tag)

        t = Tag.objects.get(name=tag)
        response = client.get(reverse('qa:tag', args=[t.id]))
        self.assertEqual(response.status_code, 200)

    def test_accept(self):
        q = create_question()
        a = create_answer(q)
        q.answers.add(a)
        client = Client()
        client.login(username=q.author.username,
                     password=default_password)
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertContains(response, reverse('qa:accept'),
                            status_code=200)
        client = Client()
        client.login(username=a.author.username,
                     password=default_password)
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertNotContains(response, reverse('qa:accept'),
                               status_code=200)

    def test_question_votes(self):
        q_votes_html = '<h2 id="question_{}">{}</h2>'
        q = create_question()
        votes = 0
        client = Client()
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertContains(response, q_votes_html.format(q.id, votes),
                            status_code=200)
        user = Profile.objects.create_user(**default_account)
        q.u_likes.add(user)
        votes = 1
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertContains(response, q_votes_html.format(q.id, votes),
                            status_code=200)
        q.u_likes.remove(user)
        q.u_dislikes.add(user)
        votes = -1
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertContains(response, q_votes_html.format(q.id, votes),
                            status_code=200)

    def test_answer_votes(self):
        a_votes_html = '<h2 id="answer_{}">{}</h2>'
        q = create_question()
        a = create_answer(q)
        q.answers.add(a)
        votes = 0
        client = Client()
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertContains(response, a_votes_html.format(a.id, votes),
                            status_code=200)
        user = Profile.objects.create_user(**default_account)
        a.u_likes.add(user)
        votes = 1
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertContains(response, a_votes_html.format(a.id, votes),
                            status_code=200)
        a.u_likes.remove(user)
        a.u_dislikes.add(user)
        votes = -1
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertContains(response, a_votes_html.format(a.id, votes),
                            status_code=200)

    def test_question_pagination(self):
        number_of_questions = settings.QUESTION_PAGINATE * 2 + 1
        user = Profile.objects.create_user(**default_account)
        for index in range(number_of_questions):
            create_question()
        client = Client()
        response = client.get(reverse('qa:questions'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['question_list']),
                         settings.QUESTION_PAGINATE)

        response = self.client.get(reverse('qa:questions')+'?page=3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['question_list']), 1)

    def test_answer_pagination(self):
        number_of_answers = settings.ANSWER_PAGINATE * 2 + 1
        user = Profile.objects.create_user(**default_account)
        q = create_question()
        for index in range(number_of_answers):
            a = create_answer(q)
            q.answers.add(a)
        client = Client()
        response = client.get(reverse('qa:detail', args=[q.id]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['items']),
                         settings.ANSWER_PAGINATE)
        response = client.get(reverse('qa:detail', args=[q.id])+'?page=3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['items']), 1)
