from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Post


class PostViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.post_data = {
            "h1": "Test H1",
            "title": "Test Title",
            "slug": "test-slug",
            "description": "Test Description",
            "content": "Test Content",
            "image": None,
            "author": self.user,
            "tags": ["tag1", "tag2"],
        }
        self.post = Post.objects.create(**self.post_data)

    def authenticate_user(self):
        self.client.login(username="testuser", password="testpassword")

    def test_delete_post(self):
        self.authenticate_user()
        response = self.client.delete(f"/api/posts/{self.post.slug}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)


class RegisterViewTests(APITestCase):
    def test_register_user(self):
        url = "/api/register/"
        data = {
            "username": "testuser",
            "password": "testpassword",
            "password2": "testpassword",
            "email": "test@example.com",
        }

        response = self.client.post(url, data, format="json")
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(username="testuser")
        self.assertEqual(response.data["user"]["username"], user.username)
        self.assertEqual(response.data["message"], "Пользователь успешно создан")
