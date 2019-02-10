import json
import pytz
from datetime import datetime
from rest_framework.test import APITestCase

from django.utils import timezone
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from hasker.qa.models import Question, Tag, Answer
from hasker.users.models import Profile
from hasker.qa.views import IndexView
from hasker.qa.forms import AddQuestionForm

from hasker.qa.qa_tests.helper import *


class ApiTest(APITestCase):
    q_num = 10
    a_num = 5

    def setUp(self):
        self.questions = [create_question() for i in range(self.q_num)]
        self.answers = [create_answer(self.questions[0]) for i in range(self.a_num)]

    def test_not_logged_get_index(self):
        client = Client()
        response = client.get(reverse('api:questions'))
        self.assertEqual(response.status_code, 401)

    def test_logged_get_index(self):
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(self.client)
        response = client.get(reverse('api:questions'))
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content.decode())
        self.assertEqual(json_resp['count'], self.q_num)

    def test_logged_get_question(self):
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(self.client)
        response = client.get(reverse('api:question_detail', args=[self.questions[0].id]))
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content.decode())
        self.assertEqual(json_resp['body'], self.questions[0].body)
        self.assertEqual(json_resp['title'], self.questions[0].title)
        self.assertEqual(len(json_resp['answers']), self.a_num)

    def test_logged_get_answers(self):
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(self.client)
        response = client.get(reverse('api:question_answers', args=[self.questions[0].id]))
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content.decode())
        self.assertEqual(len(json_resp), self.a_num)

    def test_logged_search_by_text(self):
        search_str = "adasdl2`2`2`2`23"
        self.questions[0].title = search_str
        self.questions[0].save()
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(self.client)
        response = client.get(reverse('api:search')+'?find='+search_str)
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content.decode())
        self.assertEqual(json_resp['count'], 1)
        self.assertEqual(len(json_resp['results']), 1)
        self.assertEqual(json_resp['results'][0]['title'], self.questions[0].title)
        self.assertEqual(json_resp['results'][0]['body'], self.questions[0].body)

    def test_logged_search_by_tag(self):
        search_tag = 'tag_name'
        self.questions[0].tags.add(Tag.objects.create(name='tag_name'))
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(self.client)
        response = client.get(reverse('api:search')+'?find=tag:'+search_tag)
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content.decode())
        self.assertEqual(json_resp['count'], 1)
        self.assertEqual(len(json_resp['results']), 1)
        self.assertEqual(json_resp['results'][0]['title'], self.questions[0].title)
        self.assertEqual(json_resp['results'][0]['body'], self.questions[0].body)

    def test_logged_trending(self):
        u = create_user()
        self.questions[0].u_dislikes.add(u)
        self.questions[1].u_likes.add(u)
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(self.client)
        response = client.get(reverse('api:trending'))
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content.decode())
        self.assertEqual(json_resp[0]['title'], self.questions[1].title)
        self.assertEqual(json_resp[-1]['title'], self.questions[0].title)
