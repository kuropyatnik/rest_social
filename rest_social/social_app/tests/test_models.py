from django.test import TestCase
from rest_social.social_app.models import User, Post


# Post actions: like / unlike, get all likes
class PostTestCases(TestCase):
    def setUp(self):
        # Create 3 users
        User.objects.create(username='user1', password='pwdd1598', email='ginger1@gmail.com')
        User.objects.create(username='user2', password='pwdd1598', email='ginger2@gmail.com')
        User.objects.create(username='user3', password='pwdd1598', email='ginger3@gmail.com')

        user1 = User.objects.get(username='user1')
        user2 = User.objects.get(username='user2')

        # Add two posts
        Post.objects.create(creator=user1, title='Test post 1', content='Content of test post 1')
        Post.objects.create(creator=user2, title='Test post 2', content='Content of test post 2')

        post1 = Post.objects.get(title='Test post 1')
        post1.likes.add(user1, user2)

    def test_post_liking(self):
        # Check on a duplicated user likes per one post
        user1 = User.objects.get(username='user1')
        post2 = Post.objects.get(title='Test post 2')

        post2.likes.add(user1)
        post2.likes.add(user1)

        self.assertEqual(list(post2.likes.all()), list(User.objects.filter(username__in=[user1])),
                         'Error adding like to post only once')

    def test_unlike(self):
        # Check on the unlike procedure
        user2 = User.objects.get(username='user2')
        post1 = Post.objects.get(title='Test post 1')
        previous_likes = list(post1.likes.all())

        post1.likes.remove(user2)

        self.assertNotEqual(previous_likes, list(post1.likes.all()), 'Likes are equal, unlike does not work')

    def test_user_likes(self):
        # Check all posts, that were liked by a specific user
        user1 = User.objects.get(username='user1')
        post2 = Post.objects.get(title='Test post 2')
        post2.likes.add(user1)
        self.assertEqual(list(user1.liked_posts.all()), list(Post.objects.all()), 'Error getting all likes from user')
