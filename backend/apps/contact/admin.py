from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['name', 'email', 'subject', 'message', 'ip_address', 'created_at']
    list_editable = ['is_read']

    def has_add_permission(self, request):
        """
        Disable manual creation of contact messages through admin.
        Messages should only come from the public contact form.
        """
        return False