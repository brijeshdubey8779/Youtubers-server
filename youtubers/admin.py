from django.contrib import admin
from .models import Youtubers

@admin.register(Youtubers)
class YoutubersAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'price', 'subs_count', 'is_featured', 'created_date')
    list_filter = ('category', 'crew', 'camera_type', 'is_featured', 'created_date')
    search_fields = ('name', 'city', 'description')
    list_editable = ('is_featured',)
    ordering = ('-created_date',)
    readonly_fields = ('created_date',)
