from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Tестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        model_correct_names = {
            'Тестовый пост': PostModelTest.post,
            'Тестовый слаг': PostModelTest.group
        }
        for name, models in model_correct_names.items():
            with self.subTest(name=name):
                name_post = models.__str__()
                self.assertEqual(name, name_post)

    def test_posts_correct_verbose_name(self):
        verbose_names = {
            'Текст поста': 'text',
            'Дата публикации': 'pub_date',
            'Группа': 'group',
            'Автор': 'author'
        }

        for name, post_field in verbose_names.items():
            with self.subTest(name=name):
                post = PostModelTest.post
                self.assertEqual(
                    post._meta.get_field(post_field).verbose_name, name)

    def test_posts_correct_help_text(self):
        help_texts = {
            'text': 'Введите текст',
            'group': 'Выберите группу'
        }
        for field, help_text in help_texts.items():
            with self.subTest(field=field):
                post = PostModelTest.post
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    help_text
                )
