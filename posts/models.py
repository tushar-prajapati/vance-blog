from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    CATEGORY_CHOICES = (
        ('technology', 'Technology & AI'),
        ('design', 'UI/UX Design'),
        ('architecture', 'System Architecture'),
        ('career', 'Career & Leadership'),
    )

    # Core Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='technology')
    tags = models.CharField(max_length=200, default='Tech, Design, Cloud', help_text="Comma separated tags e.g. AI, Django, CSS")
    excerpt = models.TextField(max_length=350, blank=True, help_text="Catchy teaser for article cards and hero spotlight")
    body = models.TextField()

    # Visual & Audio Assets
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True, help_text="Upload custom cover image")
    image_url = models.URLField(blank=True, help_text="Optional direct cover image URL (Unsplash, CDN, etc.)")
    audio_duration = models.CharField(max_length=30, default='4 min audio', blank=True, help_text="Audio narration duration badge")

    # Author Metadata
    author_name = models.CharField(max_length=100, default='Alexander Vance')
    author_role = models.CharField(max_length=100, default='Lead Software Architect')
    author_avatar = models.URLField(blank=True, default='https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80')

    # Metrics & Promotion
    is_featured = models.BooleanField(default=False, help_text="Feature this article in top Hero Spotlight on home page")
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=42)

    # Publishing Info
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Automatically generate unique slug from title when saving."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        # Fallback for excerpt if not filled
        if not self.excerpt and self.body:
            first_sentence = self.body.split('\n')[0].strip()
            self.excerpt = (first_sentence[:320] + '...') if len(first_sentence) > 320 else first_sentence

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'slug': self.slug})

    @property
    def get_image_url(self):
        """Returns the uploaded image URL, or direct URL, or curated aesthetic fallback."""
        if self.featured_image:
            return self.featured_image.url
        if self.image_url:
            return self.image_url
            
        defaults = {
            'technology': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80',
            'design': 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=1200&q=80',
            'architecture': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
            'career': 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80',
        }
        return defaults.get(self.category, 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1200&q=80')

    @property
    def category_badge_classes(self):
        """Returns tailored Tailwind color tokens for badges."""
        mapping = {
            'technology': 'bg-blue-50 text-blue-700 border-blue-200/80 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800/60',
            'design': 'bg-purple-50 text-purple-700 border-purple-200/80 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800/60',
            'architecture': 'bg-indigo-50 text-indigo-700 border-indigo-200/80 dark:bg-indigo-950/60 dark:text-indigo-300 dark:border-indigo-800/60',
            'career': 'bg-amber-50 text-amber-700 border-amber-200/80 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800/60',
        }
        return mapping.get(self.category, 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700')

    @property
    def tag_list(self):
        """Splits comma separated tags into clean list."""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def reading_time(self):
        """Calculates estimated reading time in minutes."""
        words = len(self.body.split())
        return max(1, round(words / 200))


class Comment(models.Model):
    """
    Reader discussion comment model with moderation flag.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"

    @property
    def avatar_initial(self):
        return self.name[0].upper() if self.name else 'A'


class NewsletterSubscriber(models.Model):
    """
    Audience lead capture subscriber model.
    """
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_subscribed']

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """
    Inbound client inquiries & work requests.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_sent']

    def __str__(self):
        return f"{self.subject} - {self.name}"
