from django.contrib import admin
from .models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'company__name')
    list_filter = ('company', 'created_at')
