import shutil
import tempfile

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm, CommentForm
from ..models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='den')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовый текст',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_date = {
            'text': 'Текст из формы',
            'group': PostsFormTest.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_date, follow=True)
        self.assertEqual(post_count + 1, Post.objects.count())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        new_post = Post.objects.all()[0]
        new_post_text = new_post.text
        new_post_author = new_post.author.username
        new_post_group = new_post.group.pk
        self.assertEqual(new_post_text, form_date['text'])
        self.assertEqual(new_post_author, PostsFormTest.user.username)
        self.assertEqual(new_post_group, form_date['group'])

    def test_change_post(self):
        post_id = PostsFormTest.post.pk
        form_date = {
            'text': 'Измененный текст из формы',
            'group': PostsFormTest.group.pk
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_date, follow=True)
        change_post_text = response.context['post'].text
        self.assertEqual(change_post_text, form_date['text'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_client_no_create_post(self):
        post_count = Post.objects.count()
        form_date = {
            'text': 'Текст из формы',
            'group': PostsFormTest.group.pk
        }

        response = self.guest_client.post(
            reverse('posts:post_create'), data=form_date, follow=True)
        new_post_count = Post.objects.count()
        reverse_login = reverse('users:login')
        reverse_post_create = reverse('posts:post_create')
        self.assertRedirects(response,
                             f"{reverse_login}?next={reverse_post_create}")
        self.assertEqual(post_count, new_post_count)

    def test_create_post_with_image(self):
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_date = {
            'text': 'Текст из формы',
            'group': PostsFormTest.group.pk,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_date, follow=True)
        new_count = Post.objects.count()
        self.assertEqual(new_count, post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostsFormTest.post.group,
                text='Текст из формы',
            ).exists()
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CommentForm()
        cls.user = User.objects.create_user(username='den2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовый текст',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=CommentFormTest.post,
            text='Какой-то комментарий',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_no_comment(self):
        count_comment = Comment.objects.count()
        form_data = {
            'text': 'Комментарий из формы'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': CommentFormTest.post.pk}),
            data=form_data,
            follow=True
        )
        new_count_comments = Comment.objects.count()
        reverse_login = reverse('users:login')
        reverse_post_create = reverse('posts:add_comment',
                                      kwargs={
                                          'post_id': CommentFormTest.post.pk}
                                      )
        self.assertRedirects(response,
                             f"{reverse_login}?next={reverse_post_create}")
        self.assertEqual(count_comment, new_count_comments)

    def test_user_add_comment(self):
        count_comment = Comment.objects.count()
        form_data = {
            'post': CommentFormTest.post.pk,
            'text': 'Комментарий из формы'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': CommentFormTest.post.pk}),
            data=form_data,
            follow=True,
        )
        new_count = Comment.objects.count()
        reverse_url = reverse(
            'posts:post_detail',
            kwargs={'post_id': CommentFormTest.post.pk})

        self.assertEqual(count_comment + 1, new_count)
        self.assertRedirects(response, reverse_url)
        # Это я бывает дополнительно проверяю еще что нить
        # Чтобы переменную респонс задействовать
        # Лучше убрать респонсе? или подобрать более
        # близкий тест?
