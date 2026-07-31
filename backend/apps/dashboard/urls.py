"""
Dashboard URL configuration.
All routes require login — enforced at the view level via
LoginRequiredMixin, not just at the URL level.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Core
    path('', views.DashboardHomeView.as_view(), name='home'),

    # Projects
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<uuid:pk>/edit/', views.ProjectUpdateView.as_view(), name='project-edit'),
    path('projects/<uuid:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),

    # Skills
    path('skills/', views.SkillListView.as_view(), name='skill-list'),
    path('skills/categories/create/', views.SkillCategoryCreateView.as_view(), name='skill-category-create'),
    path('skills/create/', views.SkillCreateView.as_view(), name='skill-create'),
    path('skills/<uuid:pk>/edit/', views.SkillUpdateView.as_view(), name='skill-edit'),
    path('skills/<uuid:pk>/delete/', views.SkillDeleteView.as_view(), name='skill-delete'),

    # Certificates
    path('certificates/', views.CertificateListView.as_view(), name='certificate-list'),
    path('certificates/create/', views.CertificateCreateView.as_view(), name='certificate-create'),
    path('certificates/<uuid:pk>/edit/', views.CertificateUpdateView.as_view(), name='certificate-edit'),
    path('certificates/<uuid:pk>/delete/', views.CertificateDeleteView.as_view(), name='certificate-delete'),

    # Experience
    path('experience/', views.ExperienceListView.as_view(), name='experience-list'),
    path('experience/create/', views.ExperienceCreateView.as_view(), name='experience-create'),
    path('experience/<uuid:pk>/edit/', views.ExperienceUpdateView.as_view(), name='experience-edit'),
    path('experience/<uuid:pk>/delete/', views.ExperienceDeleteView.as_view(), name='experience-delete'),

    # Education
    path('education/', views.EducationListView.as_view(), name='education-list'),
    path('education/create/', views.EducationCreateView.as_view(), name='education-create'),
    path('education/<uuid:pk>/edit/', views.EducationUpdateView.as_view(), name='education-edit'),
    path('education/<uuid:pk>/delete/', views.EducationDeleteView.as_view(), name='education-delete'),

    # Blog
    path('blog/', views.BlogPostListView.as_view(), name='blog-list'),
    path('blog/create/', views.BlogPostCreateView.as_view(), name='blog-create'),
    path('blog/<uuid:pk>/edit/', views.BlogPostUpdateView.as_view(), name='blog-edit'),
    path('blog/<uuid:pk>/delete/', views.BlogPostDeleteView.as_view(), name='blog-delete'),

    # Contact
    path('contact/', views.ContactMessageListView.as_view(), name='contact-list'),
    path('contact/<uuid:pk>/', views.ContactMessageDetailView.as_view(), name='contact-detail'),
    path('contact/<uuid:pk>/delete/', views.ContactMessageDeleteView.as_view(), name='contact-delete'),

    # Profile
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),

    # Auth
    path('login/', views.DashboardLoginView.as_view(), name='login'),
    path('logout/', views.DashboardLogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]