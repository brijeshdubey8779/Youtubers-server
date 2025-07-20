from django.contrib import admin
from .models import Contactpage

@admin.register(Contactpage)
class ContactpageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subject', 'created_date')
    search_fields = ('first_name', 'last_name', 'email', 'subject')
    ordering = ('-created_date',)
    readonly_fields = ('created_date',)
