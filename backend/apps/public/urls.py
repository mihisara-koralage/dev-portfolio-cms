from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'public'

urlpatterns = [
    path('',                        views.HomeView.as_view(),           name='home'),
    path('projects/',               views.ProjectListView.as_view(),     name='project-list'),
    path('projects/<slug:slug>/',   views.ProjectDetailView.as_view(),   name='project-detail'),
    path('blog/',                   views.BlogListView.as_view(),         name='blog-list'),
    path('blog/<slug:slug>/',       views.BlogDetailView.as_view(),       name='blog-detail'),
    path('certificates/',           views.CertificateListView.as_view(),  name='certificate-list'),
    path('resume/',                 views.ResumeDownloadView.as_view(),   name='resume'),
    path('contact/',                views.ContactView.as_view(),          name='contact'),

    # SEO
    path('robots.txt', TemplateView.as_view(
        template_name='public/robots.txt',
        content_type='text/plain'
    ), name='robots'),
]