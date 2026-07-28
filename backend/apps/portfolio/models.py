"""
Portfolio models: Skills, Projects, Certificates,
Work Experience, and Education.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class SkillCategory(TimeStampedModel):
    """
    Groups skills into categories displayed on the public site.
    Examples: Programming Languages, Frameworks, Cloud, DevOps.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name, e.g. 'Cloud & DevOps'."
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly version of the name. Auto-generated."
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Icon class name, e.g. 'fa-solid fa-cloud'."
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order. Lower numbers appear first."
    )

    class Meta:
        verbose_name = 'Skill Category'
        verbose_name_plural = 'Skill Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Skill(TimeStampedModel):
    """
    An individual skill belonging to a category.
    Proficiency is stored as a percentage for progress bar rendering.
    """
    PROFICIENCY_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
        ('expert',       'Expert'),
    ]

    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.CASCADE,
        related_name='skills',
        help_text="The category this skill belongs to."
    )
    name = models.CharField(
        max_length=100,
        help_text="Skill name, e.g. 'Docker', 'Python', 'AWS EC2'."
    )
    proficiency = models.CharField(
        max_length=20,
        choices=PROFICIENCY_CHOICES,
        default='intermediate',
    )
    proficiency_percent = models.PositiveSmallIntegerField(
        default=50,
        help_text="Proficiency as a percentage (0–100) for progress bars."
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Icon class or Devicons class, e.g. 'devicon-python-plain'."
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured skills are highlighted on the homepage."
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order within the category."
    )

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        ordering = ['category', 'order', 'name']
        unique_together = [['category', 'name']]

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Project(TimeStampedModel):
    """
    A portfolio project with links, tech stack, and screenshots.
    Projects can be featured to appear prominently on the homepage.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
        ('archived',    'Archived'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Project title."
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly identifier. Auto-generated from title."
    )
    short_description = models.CharField(
        max_length=300,
        help_text="One-line summary shown on project cards."
    )
    description = models.TextField(
        help_text="Full project description. Supports markdown."
    )
    thumbnail = models.ImageField(
        upload_to='projects/thumbnails/',
        null=True,
        blank=True,
        help_text="Main image shown on the project card."
    )
    github_url = models.URLField(
        blank=True,
        help_text="Link to the GitHub repository."
    )
    live_url = models.URLField(
        blank=True,
        help_text="Link to the live demo."
    )
    skills = models.ManyToManyField(
        Skill,
        through='ProjectSkill',
        related_name='projects',
        blank=True,
        help_text="Technologies used in this project."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed',
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured projects appear at the top of the portfolio."
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order. Lower numbers appear first."
    )
    started_at = models.DateField(
        null=True,
        blank=True,
        help_text="When work on this project began."
    )
    completed_at = models.DateField(
        null=True,
        blank=True,
        help_text="When the project was completed."
    )

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class ProjectSkill(models.Model):
    """
    Explicit through table for Project ↔ Skill M:M relationship.
    Using an explicit through model allows adding extra fields
    (like ordering) without replacing the relationship later.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_skills'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='project_skills'
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = [['project', 'skill']]
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} — {self.skill.name}"


class ProjectImage(TimeStampedModel):
    """
    Additional screenshots for a project.
    A project can have unlimited images; one is marked as primary.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="The project this screenshot belongs to."
    )
    image = models.ImageField(
        upload_to='projects/screenshots/',
        help_text="Screenshot or demo image."
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional caption displayed below the image."
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="The primary image is used as the project thumbnail fallback."
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Project Image'
        verbose_name_plural = 'Project Images'
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} — Image {self.order}"


class Certificate(TimeStampedModel):
    """
    A professional certification or course completion.
    """
    title = models.CharField(
        max_length=200,
        help_text="Certificate or course title."
    )
    issuing_organization = models.CharField(
        max_length=200,
        help_text="Organization that issued the certificate, e.g. 'AWS', 'Coursera'."
    )
    issue_date = models.DateField(
        help_text="Date the certificate was issued."
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date, if applicable."
    )
    credential_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="Unique credential ID provided by the issuer."
    )
    credential_url = models.URLField(
        blank=True,
        help_text="URL to verify the credential online."
    )
    image = models.ImageField(
        upload_to='certificates/',
        null=True,
        blank=True,
        help_text="Certificate image or badge."
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured certificates appear on the homepage."
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-issue_date', 'order']

    def __str__(self):
        return f"{self.title} — {self.issuing_organization}"


class WorkExperience(TimeStampedModel):
    """
    A professional work experience entry.
    end_date being null means the position is current.
    """
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. 'Remote' or 'Colombo, Sri Lanka'."
    )
    description = models.TextField(
        help_text="Responsibilities and achievements. Supports markdown."
    )
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Leave blank if this is your current position."
    )
    company_url = models.URLField(blank=True)
    company_logo = models.ImageField(
        upload_to='companies/',
        null=True,
        blank=True
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Marks this as the current position. Sets end_date display to 'Present'."
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Work Experience'
        verbose_name_plural = 'Work Experience'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.position} at {self.company}"


class Education(TimeStampedModel):
    """
    An academic qualification or degree.
    """
    institution = models.CharField(max_length=200)
    degree = models.CharField(
        max_length=200,
        help_text="e.g. 'BSc in Computer Science'."
    )
    field_of_study = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. 'Software Engineering'."
    )
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Leave blank if currently enrolled."
    )
    grade = models.CharField(
        max_length=50,
        blank=True,
        help_text="GPA, grade, or classification."
    )
    institution_url = models.URLField(blank=True)
    institution_logo = models.ImageField(
        upload_to='institutions/',
        null=True,
        blank=True
    )
    is_current = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Education'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} — {self.institution}"