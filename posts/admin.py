from django.contrib import admin
from .models import Post, Comment, NewsletterSubscriber, ContactMessage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'author_name', 'views_count', 'likes_count', 'date_created')
    list_filter = ('status', 'category', 'is_featured', 'date_created')
    search_fields = ('title', 'excerpt', 'body', 'author_name', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    
    fieldsets = (
        ('Article Content', {
            'fields': ('title', 'slug', 'category', 'tags', 'excerpt', 'body')
        }),
        ('Visual & Audio Media', {
            'fields': ('featured_image', 'image_url', 'audio_duration')
        }),
        ('Author & Meta', {
            'fields': ('author_name', 'author_role', 'author_avatar', 'is_featured', 'views_count', 'likes_count')
        }),
        ('Publishing', {
            'fields': ('status',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'date_created', 'is_approved')
    list_filter = ('is_approved', 'date_created')
    search_fields = ('name', 'email', 'content', 'post__title')
    list_editable = ('is_approved',)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed')
    search_fields = ('email',)
    date_hierarchy = 'date_subscribed'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'date_sent')
    search_fields = ('subject', 'name', 'email', 'message')
    date_hierarchy = 'date_sent'
