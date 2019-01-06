from django.test import Client, TestCase
from django.urls import reverse

from hasker.users.models import Profile

default_account = {'username': 'tany_1',
                   'email': 'email@mail.com',
                   'password': '12345_qwert'
                   }


def create_user_and_login(client, account=default_account):
    user = Profile.objects.create_user(**account)
    response = client.get(reverse('users:login'))
    post_data = {'csrfmiddlewaretoken': response.context['csrf_token'],
                 'username': account['username'],
                 'password': account['password']
                 }
    response = client.post(reverse('users:login'), post_data, follow=True)
    return response, client


def create_question(client, title, body, tags):
    response = client.get(reverse('qa:ask'), follow=True)
    post_data = {'csrfmiddlewaretoken': response.context['csrf_token'],
                 'title': title,
                 'body': body,
                 'form_tags': tags
                 }
    response = client.post(reverse('qa:ask'), post_data, follow=True)
    return response, client
