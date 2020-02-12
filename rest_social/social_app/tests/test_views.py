from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from rest_social.social_app.models import User, Post
from rest_social.settings import SECRET_KEY
import jwt


# Tests for registration request with data validating, checking for existing users, email verification
class TestRegistration(APITestCase):
    client = APIClient()

    def setUp(self):
        User.objects.create(username='user1', password=make_password('chat1597'), email='test_email1@gmail.com')
        User.objects.create(username='user2', password=make_password('chat1597'), email='test_email2@gmail.com')
        User.objects.create(username='user3', password=make_password('testpass111'), email='test_email3@gmail.com')

    def test_required_field_checking(self):
        # All fields checking
        response = self.client.post(reverse('register'),
                                    {'username': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Empty fields were submitted')

        # Email field checking
        response = self.client.post(reverse('register'),
                                    {'username': 'user1', 'password': 'blahblah56'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Abcence of the email field was ignored')

    def test_easy_password_handling(self):
        response = self.client.post(reverse('register'),
                                    {'username': 'test_user', 'password': '12345', 'email': 'blahblah@blah.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Bad password was passed')

    def test_email_validation(self):
        # Bad email
        response = self.client.post(reverse('register'),
                                    {'username': 'test_user', 'password': 'testpass111', 'email': 'email@false.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Undeliverable email was passed')
        # Good email
        response = self.client.post(reverse('register'),
                                    {'username': 'test_user', 'password': 'testpass111',
                                     'email': 'platformcs@support.facebook.com'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'New user not created')

    def test_checking_for_existing_user(self):
        # Same username
        response = self.client.post(reverse('register'),
                                    {'username': 'user1', 'password': 'testpass111', 'email': 'test_email5@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Status not 400')

        # Existing email
        response = self.client.post(reverse('register'),
                                    {'username': 'user5', 'password': 'testpass111', 'email': 'test_email1@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Duplicated email was added')

    def test_successful_registration(self):
        response = self.client.post(reverse('register'),
                                    {'username': 'gooduser', 'password': 'testpass111',
                                     'email': 'new_test_email@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'New user not created')
        self.assertTrue(User.objects.get(username='gooduser') is not None, msg='User was not saved')


# Tests for login view; jwt implementation, fields checking
class TestLoginView(APITestCase):
    def setUp(self):
        User.objects.create(username='user1', password=make_password('chat1597'), email='test_email1@gmail.com')
        User.objects.create(username='user2', password=make_password('chat1597'), email='test_email2@gmail.com')
    def test_requiredFieldChecking(self):
        response = self.client.post(reverse('login'), {'username': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Missed required field')

    def test_wrongAllCredentials(self):
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Wrong credentials passed')

    def test_wrongSomeCredentials(self):
        response = self.client.post(reverse('login'), {'username': 'user1', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Wrong password passed')

    def test_successfulAuth(self):
        response = self.client.post(reverse('login'),
                                    {'username': 'user1', 'password': 'chat1597'})

        print(response.data)
        received = jwt.decode(response.data['token'], SECRET_KEY, ['HS256'])
        expected = {
            'id': 1,
            'username': 'user1'
        }
        print(received, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Authorization failed')
        self.assertEqual(received, expected, 'JWT token failed')
