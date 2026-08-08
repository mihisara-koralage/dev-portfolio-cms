"""
XML Sitemap for the public portfolio site.
Consumed by search engine crawlers to discover all public pages.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.portfolio.models import Project
from apps.blog.models import BlogPost


class StaticViewSitemap(Sitemap):
    """Static pages that don't change often."""
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['public:home', 'public:project-list',
                'public:blog-list', 'public:certificate-list',
                'public:contact']

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('public:project-detail', args=[obj.slug])


class BlogPostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('public:blog-detail', args=[obj.slug])