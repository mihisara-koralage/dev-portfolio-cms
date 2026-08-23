"""
Blog model tests.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.blog.models import BlogCategory, BlogPost


class BlogPostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = BlogCategory.objects.create(
            name='DevOps',
            slug='devops'
        )
        self.post = BlogPost.objects.create(
            author=self.user,
            category=self.category,
            title='Getting Started with Docker',
            slug='getting-started-docker',
            content='Docker is a containerization platform. ' * 50,
            status='draft',
        )

    def test_str_returns_title(self):
        self.assertEqual(
            str(self.post),
            'Getting Started with Docker'
        )

    def test_published_at_none_when_draft(self):
        self.assertIsNone(self.post.published_at)

    def test_published_at_set_when_published(self):
        """
        published_at must be auto-set when status changes
        to published for the first time.
        """
        self.post.status = 'published'
        self.post.save()
        self.post.refresh_from_db()
        self.assertIsNotNone(self.post.published_at)

    def test_published_at_not_overwritten_on_re_save(self):
        """
        published_at must never be overwritten after
        it is first set.
        """
        self.post.status = 'published'
        self.post.save()
        first_published = self.post.published_at

        # Save again — published_at must stay the same
        self.post.title = 'Updated Title'
        self.post.save()
        self.post.refresh_from_db()
        self.assertEqual(self.post.published_at, first_published)

    def test_is_published_property(self):
        self.assertFalse(self.post.is_published)
        self.post.status = 'published'
        self.post.save()
        self.assertTrue(self.post.is_published)

    def test_reading_time_calculation(self):
        """
        reading_time should be at least 1 minute.
        50 repetitions of an 8-word sentence = ~400 words = 2 minutes.
        """
        self.assertGreaterEqual(self.post.reading_time, 1)

    def test_views_default_zero(self):
        self.assertEqual(self.post.views, 0)

    def test_only_published_posts_in_filtered_queryset(self):
        BlogPost.objects.create(
            author=self.user,
            title='Draft Post',
            slug='draft-post',
            content='Draft content.',
            status='draft',
        )
        published = BlogPost.objects.filter(status='published')
        self.assertEqual(published.count(), 0)

        self.post.status = 'published'
        self.post.save()
        published = BlogPost.objects.filter(status='published')
        self.assertEqual(published.count(), 1)