from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication URLs
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    path('auth/dashboard/', views.dashboard, name='dashboard'),
    
    # YouTubers URLs
    path('youtubers/', views.YoutubersListView.as_view(), name='youtubers_list'),
    path('youtubers/<int:pk>/', views.YoutubersDetailView.as_view(), name='youtubers_detail'),
    path('youtubers/featured/', views.FeaturedYoutubersView.as_view(), name='featured_youtubers'),
    path('youtubers/search/', views.search_youtubers, name='search_youtubers'),
    path('youtubers/inquiry/', views.YouTuberInquiryCreateView.as_view(), name='youtuber_inquiry'),
    
    # Team URLs
    path('team/', views.TeamListView.as_view(), name='team_list'),
    
    # Slider URLs
    path('sliders/', views.SliderListView.as_view(), name='slider_list'),
    
    # Contact URLs
    path('contact/', views.ContactCreateView.as_view(), name='contact_create'),
    path('contactpage/', views.ContactpageCreateView.as_view(), name='contactpage_create'),
    path('contactinfo/', views.ContactinfoListView.as_view(), name='contactinfo_list'),
    
    # Data and Stats URLs
    path('home-data/', views.home_data, name='home_data'),
    path('categories/', views.categories, name='categories'),
    path('crew-types/', views.crew_types, name='crew_types'),
    path('camera-types/', views.camera_types, name='camera_types'),
] 