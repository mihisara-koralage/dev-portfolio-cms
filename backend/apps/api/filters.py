"""
Django-filter FilterSet classes for API endpoints.

Each FilterSet maps to a ViewSet and defines exactly which
fields the client can filter on via query parameters.

Example usage:
  /api/projects/?status=completed&is_featured=true
  /api/blog/?category__slug=devops&tags__slug=docker
"""
import django_filters
from apps.portfolio.models import Project, Skill, Certificate, WorkExperience, Education
from apps.blog.models import BlogPost


class ProjectFilter(django_filters.FilterSet):
    """
    Filter projects by status, featured flag, and skill.

    /api/projects/?status=completed
    /api/projects/?is_featured=true
    /api/projects/?skills__name=Docker
    """
    status = django_filters.ChoiceFilter(
        choices=Project.STATUS_CHOICES
    )
    is_featured = django_filters.BooleanFilter()
    skills__name = django_filters.CharFilter(
        field_name='skills__name',
        lookup_expr='icontains',
        label='Skill name (partial match)'
    )
    started_after = django_filters.DateFilter(
        field_name='started_at',
        lookup_expr='gte',
        label='Started on or after'
    )
    completed_before = django_filters.DateFilter(
        field_name='completed_at',
        lookup_expr='lte',
        label='Completed on or before'
    )

    class Meta:
        model = Project
        fields = ['status', 'is_featured']


class SkillFilter(django_filters.FilterSet):
    """
    /api/skills/?category__slug=cloud-devops
    /api/skills/?is_featured=true
    /api/skills/?proficiency=expert
    """
    category__slug = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact',
        label='Category slug'
    )
    proficiency = django_filters.ChoiceFilter(
        choices=Skill.PROFICIENCY_CHOICES
    )
    is_featured = django_filters.BooleanFilter()

    class Meta:
        model = Skill
        fields = ['proficiency', 'is_featured']


class CertificateFilter(django_filters.FilterSet):
    """
    /api/certificates/?issuing_organization=AWS
    /api/certificates/?is_featured=true
    /api/certificates/?issued_after=2023-01-01
    """
    is_featured = django_filters.BooleanFilter()
    issuing_organization = django_filters.CharFilter(
        lookup_expr='icontains'
    )
    issued_after = django_filters.DateFilter(
        field_name='issue_date',
        lookup_expr='gte'
    )

    class Meta:
        model = Certificate
        fields = ['is_featured']


class BlogPostFilter(django_filters.FilterSet):
    """
    /api/blog/?category__slug=devops
    /api/blog/?tags__slug=docker
    /api/blog/?is_featured=true
    """
    category__slug = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact',
        label='Category slug'
    )
    tags__slug = django_filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='exact',
        label='Tag slug'
    )
    is_featured = django_filters.BooleanFilter()

    class Meta:
        model = BlogPost
        fields = ['is_featured']