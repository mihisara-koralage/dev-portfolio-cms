"""
Contact API endpoint tests.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.contact.models import ContactMessage


class ContactAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/contact/'

    def test_valid_submission_returns_201(self):
        response = self.client.post(self.url, {
            'name':    'Mihisara Perera',
            'email':   'mihisara@example.com',
            'subject': 'Job Opportunity',
            'message': 'Hello, I wanted to reach out regarding a position.',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('detail', response.data)

    def test_message_saved_to_database(self):
        self.client.post(self.url, {
            'name':    'Test User',
            'email':   'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message long enough to pass validation.',
        }, format='json')

        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Test User')
        self.assertFalse(msg.is_read)

    def test_message_marked_unread_by_default(self):
        self.client.post(self.url, {
            'name':    'Test User',
            'email':   'test@example.com',
            'subject': 'Test',
            'message': 'This is a long enough test message for validation.',
        }, format='json')

        msg = ContactMessage.objects.first()
        self.assertFalse(msg.is_read)

    def test_short_message_returns_400(self):
        response = self.client.post(self.url, {
            'name':    'Test User',
            'email':   'test@example.com',
            'subject': 'Hi',
            'message': 'Too short',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_short_name_returns_400(self):
        response = self.client.post(self.url, {
            'name':    'T',
            'email':   'test@example.com',
            'subject': 'Test',
            'message': 'This message is long enough to pass validation.',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_invalid_email_returns_400(self):
        response = self.client.post(self.url, {
            'name':    'Test User',
            'email':   'not-an-email',
            'subject': 'Test',
            'message': 'This message is long enough to pass validation.',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_missing_required_fields_returns_400(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name',    response.data)
        self.assertIn('email',   response.data)
        self.assertIn('subject', response.data)
        self.assertIn('message', response.data)

    def test_get_request_not_allowed(self):
        """
        The contact endpoint is write-only.
        GET must return 405 Method Not Allowed.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_ip_not_required_in_request(self):
        """
        IP address must be captured server-side,
        not accepted from the client.
        """
        response = self.client.post(self.url, {
            'name':       'Test User',
            'email':      'test@example.com',
            'subject':    'Test',
            'message':    'This message is long enough to pass validation.',
            'ip_address': '1.2.3.4',  # should be ignored
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ContactAPIProjectsTest(TestCase):
    """Tests for the projects public API."""

    def setUp(self):
        self.client = APIClient()

    def test_projects_list_returns_200(self):
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_projects_response_has_pagination_shape(self):
        response = self.client.get('/api/projects/')
        self.assertIn('pagination', response.data)
        self.assertIn('results', response.data)

    def test_skills_categories_returns_200(self):
        response = self.client.get('/api/skills/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blog_posts_returns_200(self):
        response = self.client.get('/api/blog/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_endpoint_returns_200_or_404(self):
        """
        Profile returns 404 if no profile exists yet.
        That is correct behavior, not an error.
        """
        response = self.client.get('/api/profile/')
        self.assertIn(response.status_code, [200, 404])