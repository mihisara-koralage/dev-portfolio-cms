"""
Public frontend views.

These views render HTML templates directly using querysets.
They do NOT call the REST API — both the API and these views
are separate consumers of the same underlying models.

Context processor (added below) injects profile into every
template automatically so the navbar always has the right data.
"""
import json
from django.views.generic import (
    TemplateView, ListView, DetailView, View
)
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.models import UserProfile
from apps.portfolio.models import (
    SkillCategory, Project, Certificate,
    WorkExperience, Education
)
from apps.blog.models import BlogPost, BlogCategory, Tag
from apps.contact.models import ContactMessage


class HomeView(TemplateView):
    template_name = 'public/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_projects'] = Project.objects.filter(
            is_featured=True
        ).prefetch_related('skills').order_by('order')[:6]

        context['skill_categories'] = SkillCategory.objects.prefetch_related(
            'skills'
        ).order_by('order')

        context['featured_certificates'] = Certificate.objects.filter(
            is_featured=True
        ).order_by('order')[:6]

        context['experiences'] = WorkExperience.objects.order_by(
            '-start_date'
        )[:4]

        context['education'] = Education.objects.order_by('-start_date')

        context['featured_posts'] = BlogPost.objects.filter(
            status='published',
            is_featured=True
        ).select_related('category').order_by('-published_at')[:3]

        return context


class ProjectListView(ListView):
    template_name = 'public/projects.html'
    context_object_name = 'projects'
    paginate_by = 9

    def get_queryset(self):
        qs = Project.objects.prefetch_related('skills').all()
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = Project.STATUS_CHOICES
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'public/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.prefetch_related('skills', 'images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_projects'] = Project.objects.filter(
            skills__in=self.object.skills.all()
        ).exclude(pk=self.object.pk).distinct()[:3]
        return context


class BlogListView(ListView):
    template_name = 'public/blog.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        qs = BlogPost.objects.filter(
            status='published'
        ).select_related('author', 'category').order_by('-published_at')

        category_slug = self.request.GET.get('category')
        tag_slug = self.request.GET.get('tag')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        context['tags'] = Tag.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['current_tag'] = self.request.GET.get('tag', '')
        return context


class BlogDetailView(DetailView):
    template_name = 'public/blog_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count without triggering updated_at
        BlogPost.objects.filter(pk=obj.pk).update(views=obj.views + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_posts'] = BlogPost.objects.filter(
            status='published',
            category=self.object.category
        ).exclude(pk=self.object.pk).order_by('-published_at')[:3]
        return context


class CertificateListView(ListView):
    template_name = 'public/certificates.html'
    context_object_name = 'certificates'

    def get_queryset(self):
        return Certificate.objects.order_by('-issue_date')


class ResumeDownloadView(View):
    """
    Serves the latest uploaded resume PDF as a download.
    Always fetches from the database so visitors always
    get the current version without any caching issues.
    """
    def get(self, request):
        profile = UserProfile.objects.first()
        if not profile or not profile.resume:
            raise Http404("Resume not available.")
        return FileResponse(
            profile.resume.open('rb'),
            as_attachment=True,
            filename='resume.pdf'
        )


class ContactView(TemplateView):
    """
    Contact page renders the form via template.
    Form submission is handled by the REST API endpoint
    (/api/contact/) via JavaScript fetch — this keeps the
    form submission logic in one place (the API) and gives
    us a clean JSON response without a full page reload.
    """
    template_name = 'public/contact.html'