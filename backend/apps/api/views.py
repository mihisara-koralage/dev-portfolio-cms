"""
API ViewSets.

Architecture decisions:
  - All public endpoints are read-only (RetrieveModelMixin + ListModelMixin)
    except ContactMessage which is create-only (CreateModelMixin)
  - No public endpoint allows write access to portfolio data —
    all mutations go through the dashboard
  - BlogPost detail view increments the view counter on each retrieval
  - ContactMessage captures IP address server-side, never from client input
  - Profile endpoint returns a single object, not a list
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.shortcuts import get_object_or_404

from apps.accounts.models import UserProfile
from apps.portfolio.models import (
    SkillCategory, Skill, Project,
    Certificate, WorkExperience, Education
)
from apps.blog.models import BlogPost, BlogCategory, Tag
from apps.contact.models import ContactMessage

from .serializers import (
    UserProfileSerializer,
    SkillCategorySerializer, SkillSerializer,
    ProjectListSerializer, ProjectDetailSerializer,
    CertificateSerializer,
    WorkExperienceSerializer,
    EducationSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer,
    BlogCategorySerializer, TagSerializer,
    ContactMessageSerializer,
)
from .pagination import StandardPagination, LargePagination
from .filters import (
    ProjectFilter, SkillFilter,
    CertificateFilter, BlogPostFilter
)


# ================================================================
# PROFILE
# ================================================================

@extend_schema(tags=['Profile'])
class ProfileView(APIView):
    """
    Returns the site owner's public profile.
    Single object — not a list, not paginated.
    Always returns the profile of the first superuser found.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        profile = UserProfile.objects.select_related('user').first()
        if not profile:
            return Response(
                {'detail': 'Profile not configured yet.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserProfileSerializer(
            profile,
            context={'request': request}
        )
        return Response(serializer.data)


# ================================================================
# SKILLS
# ================================================================

@extend_schema(tags=['Skills'])
@extend_schema_view(
    list=extend_schema(
        summary='List all skill categories with nested skills',
        parameters=[
            OpenApiParameter('ordering', str, description='Order by: order, name'),
        ]
    ),
    retrieve=extend_schema(summary='Get a single skill category by slug'),
)
class SkillCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Returns skill categories with all their skills nested.
    The frontend can render the entire skills section
    from a single call to /api/skills/categories/.
    """
    serializer_class = SkillCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = LargePagination
    lookup_field = 'slug'
    search_fields = ['name']
    ordering_fields = ['order', 'name']
    ordering = ['order']

    def get_queryset(self):
        return SkillCategory.objects.prefetch_related('skills').all()


@extend_schema(tags=['Skills'])
@extend_schema_view(
    list=extend_schema(
        summary='List all skills',
        parameters=[
            OpenApiParameter('category__slug', str, description='Filter by category slug'),
            OpenApiParameter('proficiency', str, description='Filter by proficiency level'),
            OpenApiParameter('is_featured', bool, description='Filter featured skills only'),
            OpenApiParameter('search', str, description='Search by skill name'),
        ]
    ),
    retrieve=extend_schema(summary='Get a single skill'),
)
class SkillViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]
    pagination_class = LargePagination
    filterset_class = SkillFilter
    search_fields = ['name']
    ordering_fields = ['order', 'name', 'proficiency_percent']
    ordering = ['category__order', 'order']

    def get_queryset(self):
        return Skill.objects.select_related('category').all()


# ================================================================
# PROJECTS
# ================================================================

@extend_schema(tags=['Projects'])
@extend_schema_view(
    list=extend_schema(
        summary='List all projects',
        parameters=[
            OpenApiParameter('status', str, description='Filter by status: in_progress, completed, archived'),
            OpenApiParameter('is_featured', bool, description='Featured projects only'),
            OpenApiParameter('skills__name', str, description='Filter by skill name'),
            OpenApiParameter('search', str, description='Search title and description'),
            OpenApiParameter('ordering', str, description='Order by: order, -created_at, title'),
        ]
    ),
    retrieve=extend_schema(summary='Get full project detail by slug'),
)
class ProjectViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    List uses ProjectListSerializer (lightweight, for cards).
    Retrieve uses ProjectDetailSerializer (full, with nested skills + images).
    Lookup is by slug, not UUID — cleaner URLs.
    """
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filterset_class = ProjectFilter
    search_fields = ['title', 'short_description', 'description']
    ordering_fields = ['order', 'created_at', 'title', 'completed_at']
    ordering = ['order', '-created_at']
    lookup_field = 'slug'

    def get_queryset(self):
        return Project.objects.prefetch_related('skills', 'images').all()

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on action.
        list   → lightweight (card data only)
        retrieve → full detail (description, nested skills, images)
        """
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectListSerializer

    @extend_schema(
        summary='List featured projects',
        tags=['Projects']
    )
    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        """
        Convenience endpoint: /api/projects/featured/
        Returns only featured projects, ordered by display order.
        Used by the homepage hero section.
        """
        qs = self.get_queryset().filter(is_featured=True).order_by('order')
        serializer = ProjectListSerializer(
            qs,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


# ================================================================
# CERTIFICATES
# ================================================================

@extend_schema(tags=['Certificates'])
@extend_schema_view(
    list=extend_schema(
        summary='List all certificates',
        parameters=[
            OpenApiParameter('is_featured', bool, description='Featured only'),
            OpenApiParameter('issuing_organization', str, description='Filter by organization'),
            OpenApiParameter('issued_after', str, description='Filter by issue date (YYYY-MM-DD)'),
            OpenApiParameter('ordering', str, description='Order by: -issue_date, order'),
        ]
    ),
    retrieve=extend_schema(summary='Get certificate detail'),
)
class CertificateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filterset_class = CertificateFilter
    search_fields = ['title', 'issuing_organization']
    ordering_fields = ['issue_date', 'order', 'title']
    ordering = ['-issue_date']

    def get_queryset(self):
        return Certificate.objects.all()

    @extend_schema(
        summary='List featured certificates',
        tags=['Certificates']
    )
    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        """Returns only featured certificates for the homepage."""
        qs = self.get_queryset().filter(is_featured=True).order_by('order')
        serializer = CertificateSerializer(
            qs,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


# ================================================================
# WORK EXPERIENCE
# ================================================================

@extend_schema(tags=['Experience'])
@extend_schema_view(
    list=extend_schema(summary='List all work experience entries'),
    retrieve=extend_schema(summary='Get work experience detail'),
)
class WorkExperienceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = WorkExperienceSerializer
    permission_classes = [AllowAny]
    pagination_class = LargePagination
    search_fields = ['company', 'position', 'description']
    ordering_fields = ['start_date', 'order']
    ordering = ['-start_date']

    def get_queryset(self):
        qs = WorkExperience.objects.all()
        is_current = self.request.query_params.get('is_current')
        if is_current is not None:
            qs = qs.filter(is_current=is_current.lower() == 'true')
        return qs


# ================================================================
# EDUCATION
# ================================================================

@extend_schema(tags=['Education'])
@extend_schema_view(
    list=extend_schema(summary='List all education entries'),
    retrieve=extend_schema(summary='Get education detail'),
)
class EducationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = EducationSerializer
    permission_classes = [AllowAny]
    pagination_class = LargePagination
    search_fields = ['institution', 'degree', 'field_of_study']
    ordering_fields = ['start_date', 'order']
    ordering = ['-start_date']

    def get_queryset(self):
        return Education.objects.all()


# ================================================================
# BLOG
# ================================================================

@extend_schema(tags=['Blog'])
@extend_schema_view(
    list=extend_schema(summary='List all blog categories'),
    retrieve=extend_schema(summary='Get blog category by slug'),
)
class BlogCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = BlogCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = LargePagination
    lookup_field = 'slug'

    def get_queryset(self):
        return BlogCategory.objects.all()


@extend_schema(tags=['Blog'])
@extend_schema_view(
    list=extend_schema(summary='List all tags'),
)
class TagViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = LargePagination

    def get_queryset(self):
        return Tag.objects.all()


@extend_schema(tags=['Blog'])
@extend_schema_view(
    list=extend_schema(
        summary='List published blog posts',
        parameters=[
            OpenApiParameter('category__slug', str, description='Filter by category slug'),
            OpenApiParameter('tags__slug', str, description='Filter by tag slug'),
            OpenApiParameter('is_featured', bool, description='Featured posts only'),
            OpenApiParameter('search', str, description='Search title, excerpt, content'),
            OpenApiParameter('ordering', str, description='Order by: -published_at, views, title'),
        ]
    ),
    retrieve=extend_schema(summary='Get full blog post by slug'),
)
class BlogPostViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Public blog endpoint.

    - Only published posts are returned (status='published')
    - Detail view increments view counter on each request
    - List uses lightweight serializer; detail uses full serializer
    - Lookup is by slug for clean URLs
    """
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filterset_class = BlogPostFilter
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'views', 'title']
    ordering = ['-published_at']
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Public endpoint only returns published posts.
        Authenticated admin users can see all posts.
        """
        if self.request.user.is_staff:
            return BlogPost.objects.select_related(
                'author', 'category'
            ).prefetch_related('tags').all()

        return BlogPost.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related('tags')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Increment view count each time a post is retrieved.
        Uses update() to avoid triggering post_save signals
        and to skip updating the updated_at timestamp.
        """
        instance = self.get_object()
        BlogPost.objects.filter(pk=instance.pk).update(
            views=instance.views + 1
        )
        instance.views += 1
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        summary='List featured blog posts',
        tags=['Blog']
    )
    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        """Returns only featured published posts for the homepage."""
        qs = self.get_queryset().filter(is_featured=True)
        serializer = BlogPostListSerializer(
            qs,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


# ================================================================
# CONTACT
# ================================================================

@extend_schema(tags=['Contact'])
class ContactMessageViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """
    Write-only endpoint for the public contact form.

    - POST /api/contact/ submits a new message
    - No GET endpoint — messages are never returned to the public
    - IP address is captured server-side from the request
    - Returns 201 on success with a confirmation message
    """
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ContactMessage.objects.none()

    @extend_schema(
        summary='Submit a contact form message',
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Message sent successfully.'
                    }
                }
            }
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Capture IP server-side — never trust client-provided IP
        ip_address = self.get_client_ip(request)
        serializer.save(ip_address=ip_address)

        return Response(
            {'detail': 'Message sent successfully. I will get back to you soon.'},
            status=status.HTTP_201_CREATED
        )

    def get_client_ip(self, request):
        """
        Extract the real client IP address.
        Checks X-Forwarded-For first (set by Nginx/load balancer),
        falls back to REMOTE_ADDR.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')