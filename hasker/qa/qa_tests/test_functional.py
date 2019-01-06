from django.test import Client, TestCase
from django.urls import reverse

from hasker.users.models import Profile
from hasker.qa.models import Question, Tag

from .helper import *


class AddQuestionTest(TestCase):

    def test_create_without_login(self):
        self.assertEqual(Question.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response, _ = create_question(client, 'Why ?', 'why ...', 't1, t2, t3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 0)

    def test_create_new_question(self):
        self.assertEqual(Question.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(client)
        self.assertEqual(response.status_code, 200)
        response, _ = create_question(client, 'Why ?', 'why ...', 't1, t2, t3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 1)

    def test_tags_creation(self):
        self.assertEqual(Tag.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(client)
        self.assertEqual(response.status_code, 200)
        response, _ = create_question(client, 'Why ?', 'why ...', 't1, t2, t3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tag.objects.count(), 3)

    def test_tags_adding(self):
        self.assertEqual(Tag.objects.count(), 0)
        self.assertEqual(Question.objects.count(), 0)
        Tag.objects.create(name='t1')
        Tag.objects.create(name='t2')
        self.assertEqual(Tag.objects.count(), 2)
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(client)
        self.assertEqual(response.status_code, 200)
        response, client = create_question(client, 'Why ?',
                                           'why ...', 't1, t2, t3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 3)
        response, client = create_question(client, 'where ?',
                                           'where ...', 't1, t1, t1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Tag.objects.count(), 3)
        response, client = create_question(client, 'What ?',
                                           'what ...', 'T1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 3)
        self.assertEqual(Tag.objects.count(), 3)
        response, client = create_question(client, 'When ?',
                                           'when ...', '   t2 , T3  ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 4)
        self.assertEqual(Tag.objects.count(), 3)
