"""
Public frontend views.

These views render HTML templates directly using querysets.
They do NOT call the REST API — both the API and these views
are separate consumers of the same underlying models.

The context processor in context_processors.py injects
site_profile into every template automatically.
"""
from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import FileResponse
from django.shortcuts import render

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
    def get(self, request):
        profile = UserProfile.objects.first()
        if not profile or not profile.resume:
            return render(request, 'public/resume_unavailable.html', status=404)
        return FileResponse(
            profile.resume.open('rb'),
            as_attachment=True,
            filename=f"{profile.full_name.replace(' ', '_')}_Resume.pdf"
        )


class ContactView(TemplateView):
    template_name = 'public/contact.html'


# ----------------------------------------------------------------
# Error handlers
# ----------------------------------------------------------------

def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)