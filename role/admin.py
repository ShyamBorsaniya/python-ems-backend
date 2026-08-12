from django.contrib import admin
from .models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'company', 'is_system_role', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'description', 'company__name')
    list_filter = ('is_system_role', 'company', 'created_at')

