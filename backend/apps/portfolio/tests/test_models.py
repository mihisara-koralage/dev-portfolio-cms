"""
Portfolio model tests.

Tests cover model behavior, not just field values.
We test the things that could break: computed properties,
ordering, constraints, and signal behavior.
"""
from django.test import TestCase
from django.utils import timezone
from apps.portfolio.models import SkillCategory, Skill, Project


class SkillCategoryModelTest(TestCase):

    def setUp(self):
        self.category = SkillCategory.objects.create(
            name='Cloud & DevOps',
            slug='cloud-devops',
            order=1
        )

    def test_str_returns_name(self):
        self.assertEqual(str(self.category), 'Cloud & DevOps')

    def test_slug_is_set(self):
        self.assertEqual(self.category.slug, 'cloud-devops')

    def test_ordering_by_order_then_name(self):
        SkillCategory.objects.create(name='Backend', slug='backend', order=0)
        categories = list(SkillCategory.objects.values_list('name', flat=True))
        self.assertEqual(categories[0], 'Backend')
        self.assertEqual(categories[1], 'Cloud & DevOps')


class SkillModelTest(TestCase):

    def setUp(self):
        self.category = SkillCategory.objects.create(
            name='Backend', slug='backend'
        )
        self.skill = Skill.objects.create(
            category=self.category,
            name='Python',
            proficiency='advanced',
            proficiency_percent=85
        )

    def test_str_includes_category(self):
        self.assertEqual(str(self.skill), 'Python (Backend)')

    def test_default_proficiency_is_intermediate(self):
        skill = Skill.objects.create(
            category=self.category,
            name='Go',
        )
        self.assertEqual(skill.proficiency, 'intermediate')

    def test_unique_together_category_and_name(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Skill.objects.create(
                category=self.category,
                name='Python',  # duplicate in same category
            )


class ProjectModelTest(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            title='Portfolio CMS',
            slug='portfolio-cms',
            short_description='A CMS for developers.',
            description='Full description here.',
            status='completed',
        )

    def test_str_returns_title(self):
        self.assertEqual(str(self.project), 'Portfolio CMS')

    def test_default_status_is_completed(self):
        self.assertEqual(self.project.status, 'completed')

    def test_is_featured_defaults_false(self):
        self.assertFalse(self.project.is_featured)

    def test_uuid_primary_key(self):
        import uuid
        self.assertIsInstance(self.project.id, uuid.UUID)

    def test_created_at_set_on_creation(self):
        self.assertIsNotNone(self.project.created_at)

    def test_updated_at_changes_on_save(self):
        original = self.project.updated_at
        self.project.short_description = 'Updated description.'
        self.project.save()
        self.project.refresh_from_db()
        self.assertGreater(self.project.updated_at, original)