"""
API URL configuration.
ViewSets and routes are registered in Module 4.2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

# ViewSets registered in Module 4.2

urlpatterns = [
    path('', include(router.urls)),
]