"""
Blog models: Categories, Tags, and Posts.

Posts support draft/published workflow.
Rich text is stored as HTML (editor handles formatting).
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TimeStampedModel


class BlogCategory(TimeStampedModel):
    """
    A category for organizing blog posts.
    Each post belongs to exactly one category.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    """
    A tag for fine-grained classification of blog posts.
    A post can have many tags; a tag can belong to many posts.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(TimeStampedModel):
    """
    A blog article with draft/published workflow.

    published_at is set automatically when status changes to
    'published' for the first time, and never overwritten.
    This preserves the original publish date even if the post
    is later edited.
    """
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT,     'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts',
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='posts',
        blank=True,
    )

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    excerpt = models.CharField(
        max_length=500,
        blank=True,
        help_text="Short summary shown on the blog listing page."
    )
    content = models.TextField(
        help_text="Full post content. Stored as HTML from the rich text editor."
    )
    cover_image = models.ImageField(
        upload_to='blog/covers/',
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set automatically when first published."
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured posts appear on the homepage."
    )
    views = models.PositiveIntegerField(
        default=0,
        help_text="View count. Incremented on each visit."
    )

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Auto-set published_at the first time status becomes 'published'.
        Never overwrite it on subsequent saves.
        """
        if self.status == self.STATUS_PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    @property
    def reading_time(self):
        """Estimates reading time based on average 200 words per minute."""
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes