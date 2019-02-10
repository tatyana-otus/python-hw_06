from django.test import Client, TestCase
from django.urls import reverse
from django.db.models import Count, F

from hasker.users.models import Profile
from hasker.qa.models import Question, Tag

from .helper import *


class AddQuestionTest(TestCase):

    def test_create_without_login(self):
        self.assertEqual(Question.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response, _ = create_question_by_http(client, 'Why ?',
                                              'why ...', 't1, t2, t3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 0)

    def test_create_new_question(self):
        self.assertEqual(Question.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(client)
        self.assertEqual(response.status_code, 200)
        response, _ = create_question_by_http(client, 'Why ?',
                                              'why ...', 't1, t2, t3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 1)

    def test_tags_creation(self):
        self.assertEqual(Tag.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response, client = create_user_and_login(client)
        self.assertEqual(response.status_code, 200)
        response, _ = create_question_by_http(client, 'Why ?',
                                              'why ...', 't1, t2, t3')
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
        response, client = create_question_by_http(client, 'Why ?',
                                                   'why ...', 't1, t2, t3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 3)
        response, client = create_question_by_http(client, 'where ?',
                                                   'where ...', 't1, t1, t1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Tag.objects.count(), 3)
        response, client = create_question_by_http(client, 'What ?',
                                                   'what ...', 'T1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 3)
        self.assertEqual(Tag.objects.count(), 3)
        response, client = create_question_by_http(client, 'When ?',
                                                   'when ...', '   t2 , T3  ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 4)
        self.assertEqual(Tag.objects.count(), 3)


class VotingTest(TestCase):
    def get_votes(self):
        q_obj = Question.objects\
                        .annotate(Count('u_likes', distinct=True),
                                  Count('u_dislikes', distinct=True))\
                        .annotate(votes=F('u_likes__count') - F('u_dislikes__count'))\
                        .get(pk=self.question.id)
        return q_obj.votes

    def setUp(self):
        self.question = create_question()
        self.client = Client(enforce_csrf_checks=True)
        response, self.client = create_user_and_login(self.client)
        response = self.client.get(reverse('qa:detail', args=[self.question.id]))
        self.assertEqual(response.status_code, 200)
        self.csrf_token = response.context['csrf_token']

    def test_logged_in_user_voting(self):
        self.assertEqual(self.get_votes(), 0)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'love',
                     'type': 'question'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "OK", "votes": 1}')
        self.assertEqual(self.get_votes(), 1)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'hate',
                     'type': 'question'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "OK", "votes": -1}')
        self.assertEqual(self.get_votes(), -1)

    def test_logged_in_user_double_love(self):
        self.assertEqual(self.get_votes(), 0)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'love',
                     'type': 'question'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "OK", "votes": 1}')
        self.assertEqual(self.get_votes(), 1)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'love',
                     'type': 'question'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "OK", "votes": 0}')
        self.assertEqual(self.get_votes(), 0)

    def test_logged_in_user_double_hate(self):
        self.assertEqual(self.get_votes(), 0)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'hate',
                     'type': 'question'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "OK", "votes": -1}')
        self.assertEqual(self.get_votes(), -1)

        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'hate',
                     'type': 'question'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "OK", "votes": 0}')
        self.assertEqual(self.get_votes(), 0)

    def test_logged_in_user_wrong_id(self):
        self.assertEqual(self.get_votes(), 0)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': 12345,
                     'value': 'love',
                     'type': 'question'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "FAIL"}')
        self.assertEqual(self.get_votes(), 0)

    def test_logged_in_user_wrong_value(self):
        self.assertEqual(self.get_votes(), 0)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'like',
                     'type': 'question'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "FAIL"}')
        self.assertEqual(self.get_votes(), 0)

    def test_logged_in_user_wrong_type(self):
        self.assertEqual(self.get_votes(), 0)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'love',
                     'type': 'qwerty'
                     }
        response = self.client.post(reverse('qa:update'), post_data)
        self.assertEqual(response.content, b'{"status": "FAIL"}')
        self.assertEqual(self.get_votes(), 0)

    def test_not_logged_in_user_voted(self):
        self.assertEqual(self.get_votes(), 0)
        c = Client()
        r = c.get(reverse('qa:detail', args=[self.question.id]))
        self.assertEqual(r.status_code, 200)
        post_data = {'csrfmiddlewaretoken': r.context['csrf_token'],
                     'id': self.question.id,
                     'value': 'love',
                     'type': 'question'
                     }
        r = c.post(reverse('qa:update'), post_data)
        self.assertEqual(r.content, b'{"status": "FAIL"}')
        self.assertEqual(self.get_votes(), 0)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.question.id,
                     'value': 'hate',
                     'type': 'question'
                     }
        r = c.post(reverse('qa:update'), post_data)
        self.assertEqual(r.content, b'{"status": "FAIL"}')
        self.assertEqual(self.get_votes(), 0)


class AcceptAnswerTest(TestCase):
    def get_accepted_answer(self):
        q_obj = Question.objects.get(pk=self.question.id)
        return q_obj.accepted_answer

    def setUp(self):
        self.question = create_question()
        self.answer_1 = create_answer(self.question)
        self.answer_2 = create_answer(self.question)
        self.client = Client(enforce_csrf_checks=True)
        self.client.login(username=self.question.author.username,
                          password=default_password)
        response = self.client.get(reverse('qa:detail', args=[self.question.id]))
        self.csrf_token = response.context['csrf_token']

    def test_question_author_double_accept_answer(self):
        self.assertEqual(self.get_accepted_answer(), None)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.answer_1.id
                     }
        response = self.client.post(reverse('qa:accept'), post_data)
        self.assertEqual(response.content, b'{"accepted": true, "status": "OK"}')
        self.assertEqual(self.get_accepted_answer(), self.answer_1)

        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.answer_1.id,
                     }
        response = self.client.post(reverse('qa:accept'), post_data)
        self.assertEqual(response.content, b'{"accepted": null, "status": "OK"}')
        self.assertEqual(self.get_accepted_answer(), None)

    def test_question_author_reaccept_answer(self):
        self.assertEqual(self.question.accepted_answer, None)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.answer_1.id,
                     }
        response = self.client.post(reverse('qa:accept'), post_data)
        self.assertEqual(response.content, b'{"accepted": true, "status": "OK"}')
        self.assertEqual(self.get_accepted_answer(), self.answer_1)

        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': self.answer_2.id,
                     }
        response = self.client.post(reverse('qa:accept'), post_data)
        self.assertEqual(response.content, b'{"accepted": true, "status": "OK"}')
        self.assertEqual(self.get_accepted_answer(), self.answer_2)

    def test_question_author_accept_invalid_answer(self):
        self.assertEqual(self.get_accepted_answer(), None)
        post_data = {'csrfmiddlewaretoken': self.csrf_token,
                     'id': 1234
                     }
        response = self.client.post(reverse('qa:accept'), post_data)
        self.assertEqual(response.content, b'{"status": "FAIL"}')
        self.assertEqual(self.get_accepted_answer(), None)

    def test_not_question_author_accept_answer(self):
        new_user = create_user()
        new_client = Client(enforce_csrf_checks=True)
        new_client.login(username=new_user.username,
                         password=default_password)
        response = new_client.get(reverse('qa:detail', args=[self.question.id]))
        self.assertEqual(self.get_accepted_answer(), None)
        post_data = {'csrfmiddlewaretoken': response.context['csrf_token'],
                     'id': self.answer_1.id
                     }
        response = new_client.post(reverse('qa:accept'), post_data)
        self.assertEqual(response.content, b'{"status": "FAIL"}')
        self.assertEqual(self.get_accepted_answer(), None)
