from django.contrib import admin
from .models import GitHubProject

@admin.register(GitHubProject)
class GitHubProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'is_hot', 'is_claimed', 'clicks_total', 'created_at', 'updated_at')
    list_filter = ('is_hot', 'is_claimed')
    search_fields = ('title', 'name', 'summary')
    ordering = ('-clicks_total',)
