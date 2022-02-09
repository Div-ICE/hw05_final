from django.test import TestCase
from ..models import Group, Post, User, Comment, Follow
from django.contrib.auth import get_user_model


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст длинной более пятнадцати символов.',
            author=cls.user,
            group=cls.group,
        )

    def test_post_str(self):
        """Проверка __str__ у post."""
        self.assertEqual(self.post.text[:Post.CONST], str(self.post))

    def test_post_verbose_name(self):
        """Проверка verbose_name у post."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа', }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = self.post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_post_help_text(self):
        """Проверка help_text у post."""
        feild_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу', }
        for value, expected in feild_help_texts.items():
            with self.subTest(value=value):
                help_text = self.post._meta.get_field(value).help_text
                self.assertEqual(help_text, expected)

    def test_post_text_str(self):
        """выводим только первые пятнадцать символов поста"""
        post = PostModelTest.post
        text = post.text
        self.assertEqual(str(post), text[:15])


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
        )

    def test_group_str(self):
        """Проверка __str__ у group."""
        self.assertEqual(self.group.title, str(self.group))

    def test_group_verbose_name(self):
        """Проверка verbose_name у group."""
        field_verboses = {
            'title': 'Название группы',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = self.group._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='text',
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        comment = CommentModelTest.comment
        comment_text = comment.text[:15]
        self.assertEqual(comment_text, str(comment))

    def test_verbose_name(self):
        """verbose_name поля text совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        verbose_text = comment._meta.get_field('text').verbose_name
        self.assertEqual(verbose_text, 'Текст комментария')

    def test_help_text(self):
        """help_text поля text совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        help_text_text = comment._meta.get_field('text').help_text
        self.assertEqual(help_text_text, 'Добавьте комментарий')


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            author=cls.username,
            user=cls.author
        )

    def test_verbose_name(self):
        """verbose_name поля text и user совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        verbose_author = follow._meta.get_field('author').verbose_name
        self.assertEqual(verbose_author, 'Автор')
        follow = FollowModelTest.follow
        verbose_user = follow._meta.get_field('user').verbose_name
        self.assertEqual(verbose_user, 'Подписчик')
