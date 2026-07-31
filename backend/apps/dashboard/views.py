"""
Dashboard views — all protected by LoginRequiredMixin.

Pattern used throughout:
- List views: display all records for that model
- Create/Update views: form handling with success messages
- Delete views: confirmation page then deletion
- All redirects stay within the dashboard namespace
"""
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import (
    TemplateView, ListView, CreateView,
    UpdateView, DeleteView, DetailView, FormView
)

from apps.accounts.models import UserProfile
from apps.portfolio.models import (
    SkillCategory, Skill, Project,
    Certificate, WorkExperience, Education
)
from apps.blog.models import BlogPost, BlogCategory, Tag
from apps.contact.models import ContactMessage

from .forms import (
    DashboardLoginForm, UserForm, UserProfileForm,
    SkillCategoryForm, SkillForm, ProjectForm,
    CertificateForm, WorkExperienceForm, EducationForm,
    BlogPostForm
)


# ----------------------------------------------------------------
# Mixins
# ----------------------------------------------------------------

class DashboardMixin(LoginRequiredMixin):
    """
    Base mixin for all dashboard views.
    Sets the login URL and adds common context.
    """
    login_url = '/dashboard/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_messages'] = ContactMessage.objects.filter(is_read=False).count()
        return context


# ----------------------------------------------------------------
# Auth views
# ----------------------------------------------------------------

class DashboardLoginView(LoginView):
    template_name = 'dashboard/auth/login.html'
    form_class = DashboardLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:home')


class DashboardLogoutView(LogoutView):
    next_page = '/dashboard/login/'


class ChangePasswordView(DashboardMixin, FormView):
    template_name = 'dashboard/auth/change_password.html'
    success_url = reverse_lazy('dashboard:profile')

    def get_form(self):
        from django.contrib.auth.forms import PasswordChangeForm
        if self.request.method == 'POST':
            return PasswordChangeForm(self.request.user, self.request.POST)
        return PasswordChangeForm(self.request.user)

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, 'Password changed successfully.')
        return super().form_valid(form)


# ----------------------------------------------------------------
# Dashboard home
# ----------------------------------------------------------------

class DashboardHomeView(DashboardMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'projects':    Project.objects.count(),
            'skills':      Skill.objects.count(),
            'certificates': Certificate.objects.count(),
            'blog_posts':  BlogPost.objects.count(),
            'published_posts': BlogPost.objects.filter(status='published').count(),
            'draft_posts': BlogPost.objects.filter(status='draft').count(),
            'messages':    ContactMessage.objects.count(),
            'unread':      ContactMessage.objects.filter(is_read=False).count(),
        }
        context['recent_messages'] = ContactMessage.objects.filter(
            is_read=False
        )[:5]
        context['recent_posts'] = BlogPost.objects.order_by('-created_at')[:5]
        return context


# ----------------------------------------------------------------
# Project views
# ----------------------------------------------------------------

class ProjectListView(DashboardMixin, ListView):
    model = Project
    template_name = 'dashboard/projects/list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        qs = Project.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs


class ProjectCreateView(DashboardMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'dashboard/projects/form.html'
    success_url = reverse_lazy('dashboard:project-list')

    def form_valid(self, form):
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
        messages.success(self.request, 'Project created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Project'
        context['action'] = 'Create'
        return context


class ProjectUpdateView(DashboardMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'dashboard/projects/form.html'
    success_url = reverse_lazy('dashboard:project-list')

    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Project'
        context['action'] = 'Update'
        return context


class ProjectDeleteView(DashboardMixin, DeleteView):
    model = Project
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:project-list')

    def form_valid(self, form):
        messages.success(self.request, 'Project deleted.')
        return super().form_valid(form)


# ----------------------------------------------------------------
# Skill views
# ----------------------------------------------------------------

class SkillListView(DashboardMixin, TemplateView):
    template_name = 'dashboard/skills/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SkillCategory.objects.prefetch_related('skills').all()
        context['category_form'] = SkillCategoryForm()
        return context


class SkillCategoryCreateView(DashboardMixin, CreateView):
    model = SkillCategory
    form_class = SkillCategoryForm
    success_url = reverse_lazy('dashboard:skill-list')

    def form_valid(self, form):
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.name)
        messages.success(self.request, 'Category created.')
        return super().form_valid(form)


class SkillCreateView(DashboardMixin, CreateView):
    model = Skill
    form_class = SkillForm
    template_name = 'dashboard/skills/form.html'
    success_url = reverse_lazy('dashboard:skill-list')

    def form_valid(self, form):
        messages.success(self.request, 'Skill added.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Skill'
        context['action'] = 'Create'
        return context


class SkillUpdateView(DashboardMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = 'dashboard/skills/form.html'
    success_url = reverse_lazy('dashboard:skill-list')

    def form_valid(self, form):
        messages.success(self.request, 'Skill updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Skill'
        context['action'] = 'Update'
        return context


class SkillDeleteView(DashboardMixin, DeleteView):
    model = Skill
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:skill-list')

    def form_valid(self, form):
        messages.success(self.request, 'Skill deleted.')
        return super().form_valid(form)


# ----------------------------------------------------------------
# Certificate views
# ----------------------------------------------------------------

class CertificateListView(DashboardMixin, ListView):
    model = Certificate
    template_name = 'dashboard/certificates/list.html'
    context_object_name = 'certificates'


class CertificateCreateView(DashboardMixin, CreateView):
    model = Certificate
    form_class = CertificateForm
    template_name = 'dashboard/certificates/form.html'
    success_url = reverse_lazy('dashboard:certificate-list')

    def form_valid(self, form):
        messages.success(self.request, 'Certificate added.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Certificate'
        context['action'] = 'Create'
        return context


class CertificateUpdateView(DashboardMixin, UpdateView):
    model = Certificate
    form_class = CertificateForm
    template_name = 'dashboard/certificates/form.html'
    success_url = reverse_lazy('dashboard:certificate-list')

    def form_valid(self, form):
        messages.success(self.request, 'Certificate updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Certificate'
        context['action'] = 'Update'
        return context


class CertificateDeleteView(DashboardMixin, DeleteView):
    model = Certificate
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:certificate-list')

    def form_valid(self, form):
        messages.success(self.request, 'Certificate deleted.')
        return super().form_valid(form)


# ----------------------------------------------------------------
# Work Experience views
# ----------------------------------------------------------------

class ExperienceListView(DashboardMixin, ListView):
    model = WorkExperience
    template_name = 'dashboard/experience/list.html'
    context_object_name = 'experiences'


class ExperienceCreateView(DashboardMixin, CreateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'dashboard/experience/form.html'
    success_url = reverse_lazy('dashboard:experience-list')

    def form_valid(self, form):
        messages.success(self.request, 'Experience added.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Experience'
        context['action'] = 'Create'
        return context


class ExperienceUpdateView(DashboardMixin, UpdateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'dashboard/experience/form.html'
    success_url = reverse_lazy('dashboard:experience-list')

    def form_valid(self, form):
        messages.success(self.request, 'Experience updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Experience'
        context['action'] = 'Update'
        return context


class ExperienceDeleteView(DashboardMixin, DeleteView):
    model = WorkExperience
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:experience-list')

    def form_valid(self, form):
        messages.success(self.request, 'Experience deleted.')
        return super().form_valid(form)


# ----------------------------------------------------------------
# Education views
# ----------------------------------------------------------------

class EducationListView(DashboardMixin, ListView):
    model = Education
    template_name = 'dashboard/education/list.html'
    context_object_name = 'education_list'


class EducationCreateView(DashboardMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = 'dashboard/education/form.html'
    success_url = reverse_lazy('dashboard:education-list')

    def form_valid(self, form):
        messages.success(self.request, 'Education entry added.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Education'
        context['action'] = 'Create'
        return context


class EducationUpdateView(DashboardMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = 'dashboard/education/form.html'
    success_url = reverse_lazy('dashboard:education-list')

    def form_valid(self, form):
        messages.success(self.request, 'Education updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Education'
        context['action'] = 'Update'
        return context


class EducationDeleteView(DashboardMixin, DeleteView):
    model = Education
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:education-list')

    def form_valid(self, form):
        messages.success(self.request, 'Education entry deleted.')
        return super().form_valid(form)


# ----------------------------------------------------------------
# Blog views
# ----------------------------------------------------------------

class BlogPostListView(DashboardMixin, ListView):
    model = BlogPost
    template_name = 'dashboard/blog/list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        qs = BlogPost.objects.select_related('author', 'category')
        status = self.request.GET.get('status')
        if status in ['draft', 'published']:
            qs = qs.filter(status=status)
        return qs


class BlogPostCreateView(DashboardMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'dashboard/blog/form.html'
    success_url = reverse_lazy('dashboard:blog-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
        messages.success(self.request, 'Post saved.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'New Post'
        context['action'] = 'Create'
        return context


class BlogPostUpdateView(DashboardMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'dashboard/blog/form.html'
    success_url = reverse_lazy('dashboard:blog-list')

    def form_valid(self, form):
        messages.success(self.request, 'Post updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Post'
        context['action'] = 'Update'
        return context


class BlogPostDeleteView(DashboardMixin, DeleteView):
    model = BlogPost
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:blog-list')

    def form_valid(self, form):
        messages.success(self.request, 'Post deleted.')
        return super().form_valid(form)


# ----------------------------------------------------------------
# Contact views
# ----------------------------------------------------------------

class ContactMessageListView(DashboardMixin, ListView):
    model = ContactMessage
    template_name = 'dashboard/contact/list.html'
    context_object_name = 'messages_list'
    paginate_by = 20

    def get_queryset(self):
        qs = ContactMessage.objects.all()
        status = self.request.GET.get('status')
        if status == 'unread':
            qs = qs.filter(is_read=False)
        elif status == 'read':
            qs = qs.filter(is_read=True)
        return qs


class ContactMessageDetailView(DashboardMixin, DetailView):
    model = ContactMessage
    template_name = 'dashboard/contact/detail.html'
    context_object_name = 'message'

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)
        if not obj.is_read:
            obj.is_read = True
            obj.save(update_fields=['is_read'])
        return obj


class ContactMessageDeleteView(DashboardMixin, DeleteView):
    model = ContactMessage
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:contact-list')

    def form_valid(self, form):
        messages.success(self.request, 'Message deleted.')
        return super().form_valid(form)


# ----------------------------------------------------------------
# Profile view
# ----------------------------------------------------------------

class ProfileUpdateView(DashboardMixin, TemplateView):
    template_name = 'dashboard/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['user_form'] = UserForm(instance=self.request.user)
        context['profile_form'] = UserProfileForm(instance=profile)
        return context

    def post(self, request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard:profile')

        return self.render_to_response(self.get_context_data(
            user_form=user_form,
            profile_form=profile_form,
        ))