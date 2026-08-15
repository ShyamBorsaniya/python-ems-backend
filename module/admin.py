from django.contrib import admin
from .models import Module


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'name', 'code', 'company', 'is_active', 'created_at')
    list_filter = ('is_active', 'company')
    search_fields = ('name', 'display_name', 'code', 'description')
