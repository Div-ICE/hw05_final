from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='post_author',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='text',
            group=cls.group,
        )
        cls.picture = (b'\x47\x49')
        cls.image = SimpleUploadedFile(
            name='small.jpg',
            content=cls.picture,
            content_type='image/jpg',
        )
        cls.comment = Comment.objects.create(
            author=cls.post_author,
            text='comment',
            post=cls.post,
        )

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)

    def test_authorized_user_create_post(self):
        """Проверка создания записи авторизированным клиентом."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])

    def test_authorized_user_edit_post(self):
        """Проверка редактирования записи авторизированным клиентом."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertTrue(post.author == self.post_author)
        self.assertTrue(post.group_id == form_data['group'])

    def test_nonauthorized_user_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_image(self):
        """Проверка изображений"""
        form_data = {
            'text': PostFormTests.post.text,
            'group': PostFormTests.group.id,
            'image': PostFormTests.image,
        }
        self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(PostFormTests.image, form_data['image'])


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='title',
            slug='test-slug',
            description='description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='text',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='comment',
            post=cls.post,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment(self):
        """Тестирование комментариев к постам."""
        comment_data = {'text': 'comment'}
        post_comment = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.comment.id}
            ),
            data=comment_data,
            follow=True
        )
        self.assertRedirects(
            post_comment,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.comment.id}
            )
        )
        self.assertEqual(CommentFormTests.comment.text, comment_data['text'])
