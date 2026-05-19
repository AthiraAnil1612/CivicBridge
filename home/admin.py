from django.contrib import admin
from django.contrib.auth.models import User
from .models import Complaint, Officer

# Register your models here.

@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ['user', 'officer_id', 'department', 'email', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['user__username', 'officer_id', 'email']
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'officer_id', 'department', 'email')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            # Only show users that are not already officers
            kwargs['queryset'] = User.objects.exclude(
                id__in=Officer.objects.values_list('user_id', flat=True)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['subject', 'citizen', 'issue_type', 'department', 'status', 'created_at']
    list_filter = ['issue_type', 'department', 'status', 'created_at']
    search_fields = ['subject', 'description', 'citizen__username', 'location']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('citizen')
