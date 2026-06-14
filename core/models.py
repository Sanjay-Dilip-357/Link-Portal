# core/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='bi-folder', help_text='Bootstrap icon class e.g. bi-bank, bi-car-front')
    color = models.CharField(max_length=7, default='#0d6efd', help_text='Hex color code')
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def link_count(self):
        return self.links.filter(is_active=True).count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Link(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('broken', 'Broken'),
        ('unknown', 'Unknown'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    url = models.URLField(max_length=500)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='links')
    tags = models.ManyToManyField(Tag, related_name='links', blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    click_count = models.PositiveIntegerField(default=0)
    link_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    last_checked = models.DateTimeField(null=True, blank=True)
    avg_rating = models.FloatField(default=0)
    total_ratings = models.IntegerField(default=0)
    favicon = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            while Link.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        if not self.favicon and self.url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(self.url)
                self.favicon = f"https://www.google.com/s2/favicons?domain={parsed.netloc}&sz=64"
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def increment_click(self):
        self.click_count += 1
        self.save(update_fields=['click_count'])


class LinkVersion(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    description = models.TextField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    change_note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.link.title} - {self.changed_at}"


class ClickLog(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='click_logs')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ['-clicked_at']


class Rating(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['link', 'session_key']


class Bookmark(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='bookmarks')
    session_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['link', 'session_key']


class Report(models.Model):
    REPORT_TYPES = [
        ('broken', 'Broken Link'),
        ('wrong_info', 'Wrong Information'),
        ('duplicate', 'Duplicate'),
        ('suggestion', 'Suggestion'),
        ('other', 'Other'),
    ]

    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    message = models.TextField()
    email = models.EmailField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_type} - {self.link}"


class Feedback(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.name or 'Anonymous'}"


class BrowsingHistory(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100)
    visited_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['link', 'session_key']
        ordering = ['-visited_at']