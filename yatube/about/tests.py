from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

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

    def test_static_urls_uses_correct_template(self):
        """URL-адреса статичных страниц использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
