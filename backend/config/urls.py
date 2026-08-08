from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.contrib.sitemaps.views import sitemap
from apps.public.sitemaps import (
    StaticViewSitemap, ProjectSitemap, BlogPostSitemap
)


admin.site.site_header = "Portfolio CMS"
admin.site.site_title = "Portfolio CMS Admin"
admin.site.index_title = "Dashboard"

sitemaps = {
    'static':   StaticViewSitemap,
    'projects': ProjectSitemap,
    'blog':     BlogPostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('api/', include('apps.api.urls', namespace='api')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Public frontend — registered last so it catches /
    path('', include('apps.public.urls', namespace='public')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Custom error handlers — must be module-level strings, not inside urlpatterns
handler404 = 'apps.public.views.handler404'
handler500 = 'apps.public.views.handler500'