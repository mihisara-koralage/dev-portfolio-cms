from django.contrib import admin
from .models import BlogCategory, Tag, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'published_at', 'views']
    list_filter = ['status', 'is_featured', 'category']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['published_at', 'views']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'excerpt', 'content', 'cover_image')
        }),
        ('Publishing', {
            'fields': ('status', 'published_at', 'is_featured', 'views')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )