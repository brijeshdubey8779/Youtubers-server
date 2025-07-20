from django.db import models
from datetime import datetime

class Contactinfo(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    fb_handle = models.CharField(max_length=255, blank=True)
    insta_handle = models.CharField(max_length=255, blank=True)
    youtube_handle = models.CharField(max_length=255, blank=True)
    twitter_handle = models.CharField(max_length=255, blank=True)
    description_1 = models.TextField(blank=True)
    description_2 = models.TextField(blank=True)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=255)
    created_date = models.DateTimeField(blank=True, default=datetime.now)

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
