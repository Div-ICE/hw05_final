from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        """Запрос к non_existing_page вернет ошибку 404"""
        response = self.client.get('/non_existing_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_error_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/non_existing_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
        # Проверьте, что статус ответа сервера - 404
        # Проверьте, что используется шаблон core/404.html
