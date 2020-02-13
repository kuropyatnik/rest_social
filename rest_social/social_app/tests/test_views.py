from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from rest_social.social_app.models import User, Post
from rest_social.settings import SECRET_KEY
import jwt


# Method for token generation
def user_token(user_id, username):
    payload = {
        'id': user_id,
        'username': username
    }
    return {'HTTP_token': jwt.encode(payload, SECRET_KEY).decode('utf-8')}


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


# Tests for post adding, data validating, fields checking
class TestAddPostView(APITestCase):

    def setUp(self):
        User.objects.create(username='user1', password=make_password('chat1597'), email='test_email1@gmail.com')
        User.objects.create(username='user2', password=make_password('chat1597'), email='test_email2@gmail.com')

    def test_Auth(self):
        response = self.client.post(reverse('add-post'),
                                    {'title': 'Post Title', 'content': 'Post content'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Problems with JWT')

    def test_FieldsValidating(self):
        response = self.client.post(reverse('add-post'),
                                    {'title': '', }, **user_token(1, 'user1'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Fields dont validate')

        response = self.client.post(reverse('add-post'),
                                    {'title': 'Post title', 'content': ''},
                                    **user_token(2, 'user2'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Adding post with empty content')

    def test_SuccessfulSending(self):
        response = self.client.post(reverse('add-post'),
                                    {'title': 'Post title', 'content': 'Post content'},
                                    **user_token(2, 'user2'))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Sending problems')

        user2 = User.objects.get(username='user2')
        self.assertTrue(Post.objects.filter(creator=user2) is not None, 'Post wasnt added')


# Tests for the entire posts set retrieving with pagination checks
class TestPostsRetrieving(APITestCase):
    def setUp(self):
        user1 = User.objects.create(username='user1', password=make_password('chat1597'), email='test_email1@gmail.com')

        # Filling posts
        for i in range(1, 25):
            Post.objects.create(creator=user1, title='Post title №{0}'.format(i), content='Message {0}'.format(i))

        post1 = Post.objects.get(title='Post title №1')
        post1.likes.add(user1)

    def test_getPageOfMessages(self):

        # Get first page by default
        response = self.client.get('http://testserver/posts/', content_type='application/json',
                                   **user_token(1, 'user1'))
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Request failed')

        # Get third page
        response = self.client.get('http://testserver/posts/?page=3', content_type='application/json',
                                   **user_token(1, 'user1'))
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Request failed')

    def test_getWrongPage(self):
        response = self.client.get('http://testserver/posts/?page=70', content_type='application/json',
                                   **user_token(1, 'user1'))
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'Wrong page showing')


# Tests for the exact post getting with existence check, and likes demonstration
class TestPostRetrieving(APITestCase):
    def setUp(self):
        user1 = User.objects.create(username='user1', password=make_password('chat1597'), email='test_email1@gmail.com')
        user2 = User.objects.create(username='user2', password=make_password('chat1597'), email='test_email2@gmail.com')

        post1 = Post.objects.create(creator=user1, title='Post title', content='Post content')
        post1.likes.add(user2)

    def test_getWrongPost(self):
        response = self.client.get('http://testserver/post/27/', **user_token(2, 'user2'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Wrong post was returned')

    def test_getPost(self):
        # Check from the liked user
        response = self.client.get('http://testserver/post/1/', content_type='application/json', **user_token(2, 'user2'))
        print(response.data)
        result = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Request failed')
        self.assertEqual(result['like'], 1, 'Like is not registered')

        # Check from the non liked user
        response = self.client.get('http://testserver/post/1/', content_type='application/json', **user_token(1, 'user1'))
        print(response.data)
        result = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Request failed')
        self.assertEqual(result['like'], 0, 'Like exists, but it doesnt need to be there')




