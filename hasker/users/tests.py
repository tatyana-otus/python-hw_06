from django.test import Client, TestCase
from django.urls import reverse

from hasker.users.models import Profile


class UsersTest(TestCase):

    def test_signup_ok(self):
        self.assertEqual(Profile.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
        post_data = {"csrfmiddlewaretoken": response.context['csrf_token'],
                     "username": "tany_1",
                     "password1": "12345_qwert",
                     "password2": "12345_qwert"}
        response = client.post(reverse('users:signup'), post_data)
        self.assertEqual(Profile.objects.count(), 1)

    def test_signup_wrong_password(self):
        self.assertEqual(Profile.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
        post_data = {"csrfmiddlewaretoken": response.context['csrf_token'],
                     "username": "tany_1",
                     "password1": "12345_qwert",
                     "password2": ""}
        response = client.post(reverse('users:signup'), post_data)
        self.assertEqual(Profile.objects.count(), 0)

    def test_login(self):
        account = {'username': 'tany_2',
                   'email': 'email@mail.com',
                   'password': '12345_qwert'}
        self.assertEqual(Profile.objects.count(), 0)
        Profile.objects.create_user(**account)
        self.assertEqual(Profile.objects.count(), 1)

        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        post_data = {'csrfmiddlewaretoken': response.context['csrf_token'],
                     'username': account['username'],
                     'password': account['password']}
        response = client.post(reverse('users:login'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_settings_if_logged_in(self):
        account = {'username': 'tany_2',
                   'email': 'email@mail.com',
                   'password': '12345_qwert'}
        user = Profile.objects.create_user(**account)
        client = Client()
        client.login(username=account['username'],
                     password=account['password'])
        response = client.get(reverse('users:settings'))
        self.assertContains(response, account['email'])
        self.assertContains(response, account['username'])

    def test_settings_redirect_if_not_logged_in(self):
        client = Client()
        response = client.get(reverse('users:settings'))
        redirect_url = reverse('users:login')+"?next="+reverse('users:settings')
        self.assertRedirects(response, redirect_url)
