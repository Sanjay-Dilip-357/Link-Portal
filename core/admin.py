# core/admin.py
from django.contrib import admin
from .models import Category, Tag, Link, LinkVersion, ClickLog, Rating, Bookmark, Report, Feedback

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'click_count', 'is_featured', 'link_status', 'is_active']
    list_filter = ['is_featured', 'link_status', 'is_active', 'categories']
    search_fields = ['title', 'url', 'description']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['link', 'report_type', 'is_resolved', 'created_at']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'message', 'is_read', 'created_at']

admin.site.register(LinkVersion)
admin.site.register(ClickLog)
admin.site.register(Rating)
admin.site.register(Bookmark)