import json
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from .models import Post, Comment, NewsletterSubscriber, ContactMessage


class PostListView(ListView):
    """
    Renders published articles in reverse chronological order.
    Supports category filtering (?category=...), tag filtering (?tag=...),
    keyword search (?q=...), and exposes hero featured story.
    """
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.filter(status='published').order_by('-date_created')

        # Category filter
        category = self.request.GET.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)


        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        # Keyword search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(body__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(author_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Hero Featured Story
        featured = Post.objects.filter(status='published', is_featured=True).first()
        if not featured:
            featured = Post.objects.filter(status='published').first()
        context['hero_post'] = featured
        
        # Current active filters
        context['current_category'] = self.request.GET.get('category', 'all')
        context['current_tag'] = self.request.GET.get('tag', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        # Category options
        context['category_list'] = [
            ('all', 'All Stories'),
            ('technology', 'Technology & AI'),
            ('design', 'UI/UX Design'),
            ('architecture', 'System Architecture'),
            ('career', 'Career & Leadership'),
        ]
        
        # Trending tags
        context['popular_tags'] = ['AI', 'Django', 'Architecture', 'Tactile UI', 'CSS', 'Cloud', 'Leadership']
        return context


class PostDetailView(DetailView):
    """
    Fetches and displays an individual published article based on its slug.
    Increments view metrics and fetches comments & related reading recommendations.
    """
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(status='published')

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        # Increment view count
        Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
        post.refresh_from_db(fields=['views_count'])
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Approved comments
        context['comments'] = post.comments.filter(is_approved=True)
        
        # 3 Related Posts in same category or latest
        related = Post.objects.filter(status='published').exclude(pk=post.pk)
        category_related = related.filter(category=post.category)[:3]
        if len(category_related) < 3:
            category_related = related[:3]
            
        context['related_posts'] = category_related
        return context


# =========================================================
# Interactive AJAX Endpoints (Likes, Comments, Newsletter)
# =========================================================

@require_POST
def like_post_api(request, slug):
    """
    AJAX endpoint to increment likes on an article.
    """
    post = get_object_or_404(Post, slug=slug, status='published')
    Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
    post.refresh_from_db(fields=['likes_count'])
    return JsonResponse({'success': True, 'likes_count': post.likes_count})


@require_POST
def add_comment_api(request, slug):
    """
    AJAX endpoint to post a reader comment.
    """
    post = get_object_or_404(Post, slug=slug, status='published')
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    content = data.get('content', '').strip()

    if not name or not email or not content:
        return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

    comment = Comment.objects.create(
        post=post,
        name=name,
        email=email,
        content=content,
        is_approved=True  # Auto-approved for frictionless demo
    )

    return JsonResponse({
        'success': True,
        'name': comment.name,
        'content': comment.content,
        'date': comment.date_created.strftime('%b %d, %Y'),
        'initial': comment.avatar_initial
    })


@require_POST
def subscribe_newsletter_api(request):
    """
    AJAX endpoint for audience lead capture.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    email = data.get('email', '').strip()
    if not email or '@' not in email:
        return JsonResponse({'success': False, 'error': 'Please enter a valid email address.'}, status=400)

    subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
    return JsonResponse({
        'success': True,
        'message': 'Welcome aboard! You have successfully subscribed to Vance Journal.'
    })
