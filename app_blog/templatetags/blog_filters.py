from django import template
from app_blog.models import Post

register = template.Library()

@register.filter(name='has_liked')
def has_liked(post, request):
    liked_posts = request.session.get('liked_posts', []) 
    return str(post.id) in liked_posts  