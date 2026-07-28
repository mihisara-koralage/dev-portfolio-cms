from django.contrib import admin
from .models import (
    SkillCategory, Skill, Project, ProjectSkill,
    ProjectImage, Certificate, WorkExperience, Education
)


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ['name', 'proficiency', 'proficiency_percent', 'is_featured', 'order']


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SkillInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'is_featured', 'order']
    list_filter = ['category', 'proficiency', 'is_featured']
    search_fields = ['name']
    list_editable = ['order', 'is_featured']


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'order']


class ProjectSkillInline(admin.TabularInline):
    model = ProjectSkill
    extra = 1
    fields = ['skill', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'is_featured', 'order', 'created_at']
    list_filter = ['status', 'is_featured']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured', 'order']
    inlines = [ProjectSkillInline, ProjectImageInline]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['title', 'issuing_organization', 'issue_date', 'is_featured']
    list_filter = ['issuing_organization', 'is_featured']
    search_fields = ['title', 'issuing_organization']
    list_editable = ['is_featured']


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    search_fields = ['company', 'position']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'start_date', 'end_date', 'is_current']
    search_fields = ['institution', 'degree']