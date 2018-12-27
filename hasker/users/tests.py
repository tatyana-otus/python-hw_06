from django.test import Client, TestCase

from hasker.users.models import Profile

class UsersTest(TestCase):

    def test_not_logged(self):
        client = Client()
        response = client.get('/questions/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_signup_ok(self):
        self.assertEqual( Profile.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response = client.get('/users/signup/')
        self.assertEqual(response.status_code, 200)
        data = {
            "csrfmiddlewaretoken": response.context['csrf_token'],
            "username": "tany_1",
            "password1": "12345_qwert",
            "password2": "12345_qwert",}
        response = client.post('/users/signup/', data)
        self.assertEqual( Profile.objects.count(), 1)

    def test_signup_wrong_password(self):
        self.assertEqual( Profile.objects.count(), 0)
        client = Client(enforce_csrf_checks=True)
        response = client.get('/users/signup/')
        self.assertEqual(response.status_code, 200)
        data = {
            "csrfmiddlewaretoken": response.context['csrf_token'],
            "username": "tany_1",
            "password1": "12345_qwert",
            "password2": "",}
        self.assertEqual( Profile.objects.count(), 0)
