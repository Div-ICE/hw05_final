from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Post, Group, Follow

User = get_user_model()


class TaskPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='TestUser')
        cls.user_following = User.objects.create_user(username='following')
        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user,
            image=SimpleUploadedFile(
                name='/posts/small.jpg/',
                content=b'\x47\x49',
                content_type='image/jpg'
            )
        )

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskPagesTest.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user_following)

    def test_pages_uses_correct_template(self):
        """проверка URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list'): 'posts/group_list.html',
            reverse(
                'posts:group',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'TestUser'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post_info(self, context):
        """Проверка корректности поста"""
        with self.subTest(context=context):
            self.assertEqual(context.text, self.post.text)
            self.assertEqual(context.pub_date, self.post.pub_date)
            self.assertEqual(context.author, self.post.author)
            self.assertEqual(context.group.id, self.post.group.id)
            self.assertEqual(context.image, self.post.image)

    def test_forms_show_correct(self):
        """Проверка коректности формы."""
        context = {
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': self.post.id,
                }
            ),
        }
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField)
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField)

    def test_index_page_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_post_info(response.context['page_obj'][0])

    def test_groups_page_correct_context(self):
        """Шаблон group.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.check_post_info(response.context['page_obj'][0])

    def test_profile_page_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}))
        self.assertEqual(response.context['author'], self.user)
        self.check_post_info(response.context['page_obj'][0])

    def test_detail_page_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        self.check_post_info(response.context['post'])
        post_title = self.post.text[:30]
        posts_count = Post.objects.filter(author=self.post.author).count()
        self.assertEqual(
            response.context['post'], 
            self.post
        )
        self.assertEqual(
            response.context['post'].text, 
            post_title
        )
        self.assertEqual(
            response.context['post'].author.posts.count(), 
            posts_count
        )
        self.assertEqual(
            response.context['post'].image,
            self.post.image
        )

    def test_create_post_with_group_displayed_correctly(self):
        """Пост с указанной группой отображается на главной странице,
        на странице группы и в профайле пользователя."""
        created_post = TaskPagesTest.post
        url_list = (
            reverse('posts:group',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': self.user}),
        )
        for value in url_list:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertIn(created_post, response.context['page_obj'])

    def test_add_new_comment(self):
        """Тест создания комментария."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': TaskPagesTest.post.id})
        )
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)

    def test_cache_index_page(self):
        """Тест кэширования главной страницы."""
        response1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.user,
            text='test-text',
            group=self.group
        )
        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response3.content, response1.content)
        self.assertEqual(response3.context['page_obj'][0].text, 'test-text')
        self.assertEqual(len(response3.context['page_obj'].object_list), 2)

    def test_follow_to_author(self):
        """"Тест подписки на автора."""
        profile_redirect = reverse('posts:profile',
                                   kwargs={'username':
                                           TaskPagesTest.user.username})
        author_follow = Follow.objects.count()
        response = self.authorized_client2.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user}
        ))
        self.assertRedirects(response, profile_redirect)
        self.assertEqual(Follow.objects.count(), author_follow + 1)

    def test_unfollow_to_author(self):
        """"Тест отписки от автора."""
        profile_redirect = reverse('posts:profile',
                                   kwargs={'username':
                                           TaskPagesTest.user.username})
        author_unfollow = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user}
        ))
        self.assertRedirects(response, profile_redirect)
        self.assertEqual(Follow.objects.count(), author_unfollow)

    def test_follow_index(self):
        """Тест страницы подписок."""
        response1 = self.authorized_client.get(reverse('posts:follow_index'))
        post1 = response1.context['page_obj']
        response2 = self.authorized_client2.get(reverse('posts:follow_index'))
        post2 = response2.context['page_obj']
        self.assertTrue(Post.objects.get(
            text=self.post.text),
            post1
        )
        self.assertNotEqual(post2, Post.objects.get(
            text=self.post.text))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='test-user',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        for i in range(13):
            Post.objects.create(
                text=f'Пост #{i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages(self):
        """Проверка паджинатора на страницах: индекс, груп, профиль"""
        posts_on_first_page = 10
        posts_on_second_page = 3
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reverse_ in url_pages:
            with self.subTest(reverse_=reverse_):
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_).context.get('page_obj')),
                    posts_on_first_page
                )
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_ + '?page=2').context.get('page_obj')),
                    posts_on_second_page
                )
