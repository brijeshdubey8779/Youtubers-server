from django.db import models

# Create your models here.

class Team(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=50)
    fb_link = models.CharField(max_length=500, blank=True)
    linkedin_link = models.CharField(max_length=500, blank=True)
    photo = models.ImageField(upload_to="team/%Y/%m/%d/")
    created_date = models.DateTimeField(auto_now_add=True)
    yt_link = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Slider(models.Model):
    headline = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=255)
    button_text = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="slider/%y/")
    created_date = models.DateTimeField(auto_now_add=True)
    button_link = models.CharField(max_length=500)

    class Meta:
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"
        ordering = ['-created_date']

    def __str__(self):
        return self.headline


class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    company_name = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class YouTuberInquiry(models.Model):
    INQUIRY_TYPES = (
        ('collaboration', 'Collaboration Request'),
        ('sponsorship', 'Sponsorship Opportunity'),
        ('interview', 'Interview Request'),
        ('event', 'Event Invitation'),
        ('general', 'General Inquiry'),
        ('business', 'Business Partnership'),
    )
    
    BUDGET_RANGES = (
        ('under_1k', 'Under $1,000'),
        ('1k_5k', '$1,000 - $5,000'),
        ('5k_10k', '$5,000 - $10,000'),
        ('10k_25k', '$10,000 - $25,000'),
        ('25k_50k', '$25,000 - $50,000'),
        ('over_50k', 'Over $50,000'),
        ('negotiable', 'Negotiable'),
    )
    
    # Foreign key to YouTuber
    youtuber = models.ForeignKey('youtubers.Youtubers', on_delete=models.CASCADE, related_name='inquiries')
    
    # Contact information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    
    # Inquiry details
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='general')
    budget_range = models.CharField(max_length=20, choices=BUDGET_RANGES, blank=True)
    project_timeline = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    # Additional information
    target_audience = models.TextField(blank=True, help_text="Describe your target audience")
    deliverables = models.TextField(blank=True, help_text="What deliverables do you expect?")
    
    # Status tracking
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('contacted', 'YouTuber Contacted'),
        ('in_discussion', 'In Discussion'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin use")

    class Meta:
        verbose_name = "YouTuber Inquiry"
        verbose_name_plural = "YouTuber Inquiries"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.youtuber.name} ({self.inquiry_type})"
