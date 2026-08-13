from django.contrib import admin
from .models import Designation


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'code', 'is_active', 'created_at')
    list_filter = ('company', 'is_active')
    search_fields = ('name', 'code', 'description')
