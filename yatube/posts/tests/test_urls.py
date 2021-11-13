from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Tестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовая группа'
        )

    def setUp(self):

        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        url_post_id = f'/posts/{PostURLTests.post.pk}/'
        """URL-адрес использует соответствующий шаблон"""
        url_index = '/'
        url_group = '/group/test-slug/'
        url_profile = '/profile/auth/'
        url_follow = '/follow/'
        templates_url_names = {
            url_follow: 'posts/follow.html',
            url_index: 'posts/index.html',
            url_group: 'posts/group_list.html',
            url_profile: 'posts/profile.html',
            url_post_id: 'posts/post_detail.html',
        }

        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_url_author_edit(self):
        post_id = PostURLTests.post.pk
        response = self.authorized_client.get(
            f'/posts/{post_id}/edit/', follow=True)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_url_create(self):
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_unexist_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
