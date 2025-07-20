from django.db import models
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
