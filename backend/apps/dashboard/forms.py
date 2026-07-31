"""
Dashboard forms for all CMS operations.
Each form maps directly to a model with field-level validation.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User

from apps.accounts.models import UserProfile
from apps.portfolio.models import (
    SkillCategory, Skill, Project, ProjectImage,
    Certificate, WorkExperience, Education
)
from apps.blog.models import BlogCategory, Tag, BlogPost
from apps.contact.models import ContactMessage


# ----------------------------------------------------------------
# Auth forms
# ----------------------------------------------------------------

class DashboardLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-600 text-white focus:outline-none focus:border-blue-500',
        'placeholder': 'Username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-600 text-white focus:outline-none focus:border-blue-500',
        'placeholder': 'Password',
    }))


# ----------------------------------------------------------------
# Profile form
# ----------------------------------------------------------------

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user', 'created_at', 'updated_at', 'id']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }


# ----------------------------------------------------------------
# Portfolio forms
# ----------------------------------------------------------------

class SkillCategoryForm(forms.ModelForm):
    class Meta:
        model = SkillCategory
        fields = ['name', 'slug', 'icon', 'order']


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['category', 'name', 'proficiency', 'proficiency_percent',
                  'icon', 'is_featured', 'order']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'slug', 'short_description', 'description',
            'thumbnail', 'github_url', 'live_url', 'skills',
            'status', 'is_featured', 'order', 'started_at', 'completed_at'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'started_at': forms.DateInput(attrs={'type': 'date'}),
            'completed_at': forms.DateInput(attrs={'type': 'date'}),
            'skills': forms.CheckboxSelectMultiple(),
        }


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption', 'is_primary', 'order']


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            'title', 'issuing_organization', 'issue_date', 'expiry_date',
            'credential_id', 'credential_url', 'image', 'is_featured', 'order'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = [
            'company', 'position', 'location', 'description',
            'start_date', 'end_date', 'company_url',
            'company_logo', 'is_current', 'order'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            'institution', 'degree', 'field_of_study', 'description',
            'start_date', 'end_date', 'grade',
            'institution_url', 'institution_logo', 'is_current', 'order'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


# ----------------------------------------------------------------
# Blog forms
# ----------------------------------------------------------------

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'category', 'tags', 'excerpt',
            'content', 'cover_image', 'status', 'is_featured',
            'meta_title', 'meta_description'
        ]
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 20,
                'id': 'blog-content-editor',
            }),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
            'tags': forms.CheckboxSelectMultiple(),
        }