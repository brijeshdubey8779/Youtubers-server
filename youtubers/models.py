from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Youtubers(models.Model):
    crew_choices = (
        ("solo", "Solo"),
        ("small", "Small Team"),
        ("large", "Large Team"),
    )

    camera_choices = (
        ("canon", "Canon"),
        ("nikon", "Nikon"),
        ("sony", "Sony"),
        ("red", "RED"),
        ("fuji", "Fujifilm"),
        ("panasonic", "Panasonic"),
        ("other", "Other"),
    )

    category_choices = (
        ("code", "Coding"),
        ("mobile_review", "Mobile Review"),
        ("vlogs", "Vlogs"),
        ("comedy", "Comedy"),
        ("gaming", "Gaming"),
        ("standup", "Stand-up"),
        ("anime", "Anime"),
        ("film_making", "Film Making"),
        ("song", "Music"),
        ("motivation", "Motivation"),
        ("cooking", "Cooking"),
        ("other", "Other"),
    )

    # User authentication relationship (optional for existing YouTubers)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='youtuber_profile')
    
    # Creator authentication fields
    creator_email = models.EmailField(unique=True, null=True, blank=True, help_text="Email for creator dashboard login")
    creator_username = models.CharField(max_length=150, unique=True, null=True, blank=True, help_text="Username for creator dashboard")
    is_creator_verified = models.BooleanField(default=False, help_text="Whether creator account is verified")
    can_manage_inquiries = models.BooleanField(default=True, help_text="Whether creator can manage their own inquiries")
    
    # Original YouTuber fields
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    photo = models.ImageField(upload_to="youtubers/%Y/%m/")
    video_url = models.CharField(max_length=255)
    description = models.TextField()
    city = models.CharField(max_length=255)
    age = models.IntegerField()
    height = models.IntegerField()
    crew = models.CharField(choices=crew_choices, max_length=255)
    camera_type = models.CharField(choices=camera_choices, max_length=255)
    subs_count = models.CharField(max_length=255)
    category = models.CharField(choices=category_choices, max_length=255)
    is_featured = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        verbose_name = "YouTuber"
        verbose_name_plural = "YouTubers"
        ordering = ['-created_date']

    def __str__(self):
        return self.name
    
    @property
    def has_creator_account(self):
        """Check if YouTuber has a creator account"""
        return self.user is not None
    
    @property
    def pending_inquiries_count(self):
        """Count of pending inquiries"""
        return self.inquiries.filter(status='pending').count()
    
    @property
    def total_inquiries_count(self):
        """Total count of all inquiries"""
        return self.inquiries.count()
