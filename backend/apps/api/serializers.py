"""
API Serializers.

Serializers sit between the database models and the API responses.
They control:
  - Which fields are exposed publicly
  - How related objects are represented (nested vs flat)
  - Read-only vs writable fields
  - Computed/property fields

Design rules applied here:
  - Never expose internal fields (created_at on public endpoints is fine,
    but things like ip_address on ContactMessage are write-only)
  - Use nested serializers for related objects the frontend always needs
  - Use SerializerMethodField for computed properties (reading_time, etc.)
  - Keep list serializers lighter than detail serializers
"""
from rest_framework import serializers
from apps.accounts.models import UserProfile
from apps.portfolio.models import (
    SkillCategory, Skill, Project,
    ProjectImage, Certificate, WorkExperience, Education
)
from apps.blog.models import BlogCategory, Tag, BlogPost
from apps.contact.models import ContactMessage


# ================================================================
# PROFILE SERIALIZERS
# ================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Full profile serializer for the site owner.
    Used by the public /api/profile/ endpoint.
    """
    full_name = serializers.ReadOnlyField()
    has_resume = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = [
            'full_name',
            'title',
            'bio',
            'location',
            'years_of_experience',
            'profile_picture',
            'github_url',
            'linkedin_url',
            'twitter_url',
            'website_url',
            'email',
            'has_resume',
            'meta_description',
        ]


# ================================================================
# SKILL SERIALIZERS
# ================================================================

class SkillSerializer(serializers.ModelSerializer):
    """Individual skill with proficiency data for progress bars."""
    proficiency_display = serializers.CharField(
        source='get_proficiency_display',
        read_only=True
    )
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    class Meta:
        model = Skill
        fields = [
            'id',
            'name',
            'category_name',
            'proficiency',
            'proficiency_display',
            'proficiency_percent',
            'icon',
            'is_featured',
            'order',
        ]


class SkillCategorySerializer(serializers.ModelSerializer):
    """
    Skill category with all its skills nested.
    This allows the frontend to render the full skills section
    in a single API call rather than N+1 requests.
    """
    skills = SkillSerializer(many=True, read_only=True)
    skill_count = serializers.SerializerMethodField()

    class Meta:
        model = SkillCategory
        fields = [
            'id',
            'name',
            'slug',
            'icon',
            'order',
            'skill_count',
            'skills',
        ]

    def get_skill_count(self, obj):
        return obj.skills.count()


# ================================================================
# PROJECT SERIALIZERS
# ================================================================

class ProjectImageSerializer(serializers.ModelSerializer):
    """Screenshot for a project."""

    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'caption', 'is_primary', 'order']


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Lightweight project serializer for the listing page.
    Does not include full description or all images —
    only what's needed to render project cards.
    """
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    skill_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'slug',
            'short_description',
            'thumbnail',
            'github_url',
            'live_url',
            'status',
            'status_display',
            'is_featured',
            'order',
            'skill_names',
            'started_at',
            'completed_at',
        ]

    def get_skill_names(self, obj):
        return list(obj.skills.values_list('name', flat=True))


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Full project serializer for the detail page.
    Includes nested skills and all screenshots.
    """
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    skills = SkillSerializer(many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'slug',
            'short_description',
            'description',
            'thumbnail',
            'github_url',
            'live_url',
            'skills',
            'images',
            'status',
            'status_display',
            'is_featured',
            'order',
            'started_at',
            'completed_at',
            'created_at',
        ]


# ================================================================
# CERTIFICATE SERIALIZERS
# ================================================================

class CertificateSerializer(serializers.ModelSerializer):
    """Full certificate serializer — used for both list and detail."""
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            'id',
            'title',
            'issuing_organization',
            'issue_date',
            'expiry_date',
            'credential_id',
            'credential_url',
            'image',
            'is_featured',
            'order',
            'is_expired',
        ]

    def get_is_expired(self, obj):
        """Returns True if the certificate has an expiry date in the past."""
        if not obj.expiry_date:
            return False
        from django.utils import timezone
        return obj.expiry_date < timezone.now().date()


# ================================================================
# WORK EXPERIENCE SERIALIZERS
# ================================================================

class WorkExperienceSerializer(serializers.ModelSerializer):
    """Work experience entry with computed duration."""
    duration = serializers.SerializerMethodField()

    class Meta:
        model = WorkExperience
        fields = [
            'id',
            'company',
            'position',
            'location',
            'description',
            'start_date',
            'end_date',
            'company_url',
            'company_logo',
            'is_current',
            'order',
            'duration',
        ]

    def get_duration(self, obj):
        """
        Returns a human-readable duration string.
        e.g. '2 years, 3 months' or '8 months'
        """
        from django.utils import timezone
        end = timezone.now().date() if obj.is_current else obj.end_date
        if not end:
            return None
        delta_months = (
            (end.year - obj.start_date.year) * 12
            + (end.month - obj.start_date.month)
        )
        years, months = divmod(delta_months, 12)
        parts = []
        if years:
            parts.append(f"{years} year{'s' if years != 1 else ''}")
        if months:
            parts.append(f"{months} month{'s' if months != 1 else ''}")
        return ', '.join(parts) if parts else 'Less than a month'


# ================================================================
# EDUCATION SERIALIZERS
# ================================================================

class EducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Education
        fields = [
            'id',
            'institution',
            'degree',
            'field_of_study',
            'description',
            'start_date',
            'end_date',
            'grade',
            'institution_url',
            'institution_logo',
            'is_current',
            'order',
        ]


# ================================================================
# BLOG SERIALIZERS
# ================================================================

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class BlogCategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()


class BlogPostListSerializer(serializers.ModelSerializer):
    """
    Lightweight post serializer for the blog listing page.
    Does not include full content — only card data.
    """
    author_name = serializers.SerializerMethodField()
    category = BlogCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time = serializers.ReadOnlyField()

    class Meta:
        model = BlogPost
        fields = [
            'id',
            'title',
            'slug',
            'excerpt',
            'cover_image',
            'author_name',
            'category',
            'tags',
            'status',
            'is_featured',
            'published_at',
            'views',
            'reading_time',
        ]

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """
    Full post serializer for the post detail page.
    Includes full content, nested relations, and SEO fields.
    """
    author_name = serializers.SerializerMethodField()
    category = BlogCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time = serializers.ReadOnlyField()

    class Meta:
        model = BlogPost
        fields = [
            'id',
            'title',
            'slug',
            'excerpt',
            'content',
            'cover_image',
            'author_name',
            'category',
            'tags',
            'status',
            'is_featured',
            'published_at',
            'views',
            'reading_time',
            'meta_title',
            'meta_description',
        ]

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None


# ================================================================
# CONTACT SERIALIZER
# ================================================================

class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Write-only serializer for contact form submissions.

    Notice what is NOT included in fields:
      - is_read (internal admin field)
      - ip_address (set server-side, never from client)
      - created_at (set automatically)

    This serializer is write-only — it is never used to
    return contact message data to the public.
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def validate_message(self, value):
        """Enforce a minimum message length to reduce spam."""
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                "Message must be at least 20 characters."
            )
        return value

    def validate_name(self, value):
        """Basic sanity check on name field."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Please enter your full name."
            )
        return value