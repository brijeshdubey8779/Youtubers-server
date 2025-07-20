from django.contrib import admin
from .models import Team, Slider, Contact, YouTuberInquiry

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'created_date')
    search_fields = ('first_name', 'last_name', 'role')
    ordering = ('-created_date',)
    readonly_fields = ('created_date',)

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('headline', 'subtitle', 'button_text', 'created_date')
    search_fields = ('headline', 'subtitle')
    ordering = ('-created_date',)
    readonly_fields = ('created_date',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'created_at')
    search_fields = ('full_name', 'email', 'subject')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(YouTuberInquiry)
class YouTuberInquiryAdmin(admin.ModelAdmin):
    list_display = (
        'get_full_name', 'youtuber', 'inquiry_type', 'budget_range', 
        'status', 'created_at', 'email'
    )
    list_filter = (
        'inquiry_type', 'budget_range', 'status', 'created_at', 
        'youtuber__category'
    )
    search_fields = (
        'first_name', 'last_name', 'email', 'company_name', 
        'subject', 'youtuber__name'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'company_name', 'website')
        }),
        ('Inquiry Details', {
            'fields': ('youtuber', 'inquiry_type', 'budget_range', 'project_timeline', 'subject', 'message')
        }),
        ('Project Information', {
            'fields': ('target_audience', 'deliverables'),
            'classes': ('collapse',)
        }),
        ('Status & Admin', {
            'fields': ('status', 'admin_notes', 'created_at', 'updated_at')
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('youtuber')
    
    actions = ['mark_as_contacted', 'mark_as_in_discussion', 'mark_as_accepted']
    
    def mark_as_contacted(self, request, queryset):
        queryset.update(status='contacted')
        self.message_user(request, f"{queryset.count()} inquiries marked as contacted.")
    mark_as_contacted.short_description = "Mark selected inquiries as contacted"
    
    def mark_as_in_discussion(self, request, queryset):
        queryset.update(status='in_discussion')
        self.message_user(request, f"{queryset.count()} inquiries marked as in discussion.")
    mark_as_in_discussion.short_description = "Mark selected inquiries as in discussion"
    
    def mark_as_accepted(self, request, queryset):
        queryset.update(status='accepted')
        self.message_user(request, f"{queryset.count()} inquiries marked as accepted.")
    mark_as_accepted.short_description = "Mark selected inquiries as accepted"
