from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import Group, Post
from users.forms import User


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        """Проверка доступности адреса /."""
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about(self):
        """Проверка доступности адреса /about/author/."""
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        """Проверка доступности адреса /about/tech/."""
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class URLsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug'
        )
        cls.user = User.objects.create(username='test-user')
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )
        cls.user2 = User.objects.create(username='test-user2')

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        # self.user = User.objects.create_user(username='test-user')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(URLsTests.user)

    def test_index_url_exists_for_all(self):
        """Страница / доступна любому пользователю"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_posts_exists_for_all(self):
        """Страница /group/slug/ доступна любому пользователю"""
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_exists_for_all(self):
        """Страница /profile/ доступна любому пользователю"""
        response = self.guest_client.get(f'/profile/{self.user}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_url_exists_for_all(self):
        """Страница /post/{self.post.id}/ доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_for_author(self):
        """Страница /posts/{post_id}/edit/ доступна автору."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_for_authorized(self):
        """/posts/create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_not_exists_for_noauthorized(self):
        """/posts/create/ не доступна неавторизованному пользователю."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_follow_url_not_exists_for_noauthorized(self):
        """/follow/ не доступна неавторизованному пользователю."""
        response = self.guest_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_not_exists_for_noauthorized(self):
        """/posts/{post_id}/edit/ недоступна не авторизованному пользователю"""
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page(self):
        """Запрос к unixisting_page вернет ошибку 404"""
        response = self.guest_client.get('/unixisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/post_create.html',
            f'/group/{self.group.slug}/': 'posts/group.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            '/follow/': 'posts/follow.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_not_exist_for_not_author(self):
        """Страница /posts/{post_id}/edit/ недоступна  не автору."""
        self.user_other = User.objects.create_user(username='test-user-other')
        self.authorized_client_other = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user_other)
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
