from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'country')
    search_fields = ('name', 'code', 'email', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')
