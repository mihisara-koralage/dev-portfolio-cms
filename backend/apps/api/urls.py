"""
API URL configuration.

Uses DRF's DefaultRouter which auto-generates:
  /api/{prefix}/           → list
  /api/{prefix}/{lookup}/  → detail

Custom actions registered with @action are added automatically:
  /api/projects/featured/
  /api/blog/posts/featured/
  /api/certificates/featured/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()

# Profile — single object view, registered manually below
# Skills
router.register(r'skills/categories', views.SkillCategoryViewSet, basename='skill-category')
router.register(r'skills',            views.SkillViewSet,          basename='skill')

# Projects
router.register(r'projects', views.ProjectViewSet, basename='project')

# Certificates
router.register(r'certificates', views.CertificateViewSet, basename='certificate')

# Experience & Education
router.register(r'experience', views.WorkExperienceViewSet, basename='experience')
router.register(r'education',  views.EducationViewSet,      basename='education')

# Blog
router.register(r'blog/categories', views.BlogCategoryViewSet, basename='blog-category')
router.register(r'blog/tags',       views.TagViewSet,          basename='blog-tag')
router.register(r'blog/posts',      views.BlogPostViewSet,     basename='blog-post')

# Contact
router.register(r'contact', views.ContactMessageViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),

    # Profile is a single-object endpoint, not a ViewSet
    path('profile/', views.ProfileView.as_view(), name='profile'),
]