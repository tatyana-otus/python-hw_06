from django.test import Client, TestCase
from django.urls import reverse

from hasker.users.models import Profile
from hasker.qa.models import Question, Tag


def create_user_and_login(client):
    account = {'username': 'tany_1',
               'email': 'email@mail.com',
               'password': '12345_qwert'
               }
    user = Profile.objects.create_user(**account)
    response = client.get(reverse('users:login'))
    post_data = {'csrfmiddlewaretoken': response.context['csrf_token'],
                 'username': account['username'],
                 'password': account['password']
                 }
    response = client.post(reverse('users:login'), post_data, follow=True)
    return client


def create_question(client, title, body, tags):
    response = client.get(reverse('qa:ask'), follow=True)
    post_data = {'csrfmiddlewaretoken': response.context['csrf_token'],
                 'title': title,
                 'body': body,
                 'form_tags': tags
                 }
    response = client.post(reverse('qa:ask'), post_data, follow=True)


class AddQuestionTest(TestCase):

    def test_create_without_login(self):
        self.assertEqual(Question.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        create_question(client, 'Why ?', 'why ...', 't1, t2, t3')
        self.assertEqual(Question.objects.count(), 0)

    def test_create_new_question(self):
        self.assertEqual(Question.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        client = create_user_and_login(client)
        create_question(client, 'Why ?', 'why ...', 't1, t2, t3')
        self.assertEqual(Question.objects.count(), 1)

    def test_tags_creation(self):
        self.assertEqual(Tag.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        client = create_user_and_login(client)
        create_question(client, 'Why ?', 'why ...', 't1, t2, t3')
        self.assertEqual(Tag.objects.count(), 3)

    def test_tags_adding(self):
        self.assertEqual(Tag.objects.count(), 0)
        self.assertEqual(Question.objects.count(), 0)
        Tag.objects.create(name='t1')
        Tag.objects.create(name='t2')
        self.assertEqual(Tag.objects.count(), 2)
        client = Client(enforce_csrf_checks=True)
        client = create_user_and_login(client)
        create_question(client, 'Why ?', 'why ...', 't1, t2, t3')
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 3)
        create_question(client, 'where ?', 'where ...', 't1, t1, t1')
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Tag.objects.count(), 3)
        create_question(client, 'What ?', 'what ...', 'T1')
        self.assertEqual(Question.objects.count(), 3)
        self.assertEqual(Tag.objects.count(), 3)
        create_question(client, 'When ?', 'when ...', '   t2 , T3  ')
        self.assertEqual(Question.objects.count(), 4)
        self.assertEqual(Tag.objects.count(), 3)
