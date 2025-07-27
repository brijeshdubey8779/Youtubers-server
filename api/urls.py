from django.urls import path
from . import views

urlpatterns = [
    # Home and content
    path('home/', views.home_data, name='home_data'),
    path('contact-info/', views.ContactinfoListView.as_view(), name='contact_info'),

    # ==================== REGULAR USER AUTHENTICATION URLs ====================
    
    # Regular User Authentication
    path('auth/register/', views.register, name='user_register'),
    path('auth/login/', views.login, name='user_login'),
    path('auth/dashboard/', views.dashboard, name='user_dashboard'),
    path('auth/profile/', views.user_profile, name='user_profile'),

    # YouTubers
    path('youtubers/', views.YoutubersListView.as_view(), name='youtubers_list'),
    path('youtubers/<int:pk>/', views.YoutubersDetailView.as_view(), name='youtubers_detail'),
    path('youtubers/featured/', views.FeaturedYoutubersView.as_view(), name='featured_youtubers'),
    
    # Contact and inquiries
    path('contactpage/', views.ContactpageCreateView.as_view(), name='contactpage_create'),
    path('youtubers/inquiry/', views.YouTuberInquiryCreateView.as_view(), name='youtuber_inquiry'),
    
    # Team and sliders
    path('team/', views.TeamListView.as_view(), name='team_list'),
    path('sliders/', views.SliderListView.as_view(), name='slider_list'),
    
    # ==================== CREATOR AUTHENTICATION URLs ====================
    
    # Creator Authentication
    path('creator/register/', views.CreatorRegistrationView.as_view(), name='creator_register'),
    path('creator/login/', views.CreatorLoginView.as_view(), name='creator_login'),
    path('creator/logout/', views.CreatorLogoutView.as_view(), name='creator_logout'),
    
    # Creator Dashboard
    path('creator/dashboard/', views.CreatorDashboardView.as_view(), name='creator_dashboard'),
    path('creator/profile/', views.CreatorProfileUpdateView.as_view(), name='creator_profile_update'),
    
    # Creator Inquiry Management
    path('creator/inquiries/', views.CreatorInquiriesListView.as_view(), name='creator_inquiries_list'),
    path('creator/inquiries/<int:pk>/', views.CreatorInquiryDetailView.as_view(), name='creator_inquiry_detail'),
    path('creator/inquiries/<int:pk>/status/', views.CreatorInquiryStatusUpdateView.as_view(), name='creator_inquiry_status_update'),
] 