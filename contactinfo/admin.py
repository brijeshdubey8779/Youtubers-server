from django.contrib import admin
from .models import Contactinfo

@admin.register(Contactinfo)
class ContactinfoAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'created_date')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('created_date',)
