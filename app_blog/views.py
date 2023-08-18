from django.shortcuts import redirect, render
from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag


class BlogView(View):
    template = 'blog_main.html'

    def get(self, request):
        query = request.GET.get('q')
        categories = Category.objects.all().order_by('name')
        tags = Tag.objects.all()
        if query:
            main_post = None
            posts = Post.objects.filter(title__icontains=query, status=1).order_by('-created_at')
        else:
            main_post = Post.objects.filter(status=1).order_by('-created_at').first()
            posts = Post.objects.filter(status=1).exclude(id=main_post.id).order_by('-created_at')

        context = {'main_post': main_post, 
                   'posts': posts,
                   'categories': categories,
                   'tags': tags}
        return render(request, self.template, context)


class TagSearchView(View):
    template_name = 'blog_main.html'

    def get(self, request, tag):
        posts = Post.objects.filter(tags__tag__iexact=tag, status=1).order_by('-created_at')
        categories = Category.objects.all().order_by('name')
        tags = Tag.objects.all()
        context = {'search': True,
                   'tag': tag, 
                   'posts': posts,
                   'categories': categories,
                   'tags': tags}
        return render(request, self.template_name, context)
    

class CategorySearchView(View):
    template_name = 'blog_main.html'

    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        tags = Tag.objects.all()
        posts = Post.objects.filter(categories=category, status=1).order_by('-created_at')
        categories = Category.objects.all().order_by('name')
        context = {
            'search': True,
            'category_search': True,
            'posts': posts,
            'categories': categories,
            'category': category,
            'tags': tags
        }
        return render(request, self.template_name, context)


class PostDetailView(View):


    template_name = 'blog_post.html'

    def get(self, request, slug):
        """
        Gets the selected post and the related posts
        """

        post = get_object_or_404(Post, slug=slug, status=1)
        related_posts = Post.objects.filter(
            categories__in=post.categories.all(), status=1).exclude(id=post.id).order_by('-visits')[:4]
        
        # Verify if current session has visited the post, if not adds +1 to visits
        if not request.session.get(f'visited_post_{post.id}'):
            post.visits += 1
            post.save()
            request.session[f'visited_post_{post.id}'] = True
        context = {'post': post, 'related_posts': related_posts}
        return render(request, self.template_name, context)
    
    def post(self, request, slug):
        post = Post.objects.get(slug=slug)

        submit_action = request.POST.get('submit_action')
        #Verifys if current session has liked the post, if not adds +1 to likes, works together with the templatetag 'has_liked'
        if submit_action == 'like_submit':
            liked_posts = request.session.get('liked_posts', [])
            if str(post.id) not in liked_posts:
                liked_posts.append(str(post.id))
                request.session['liked_posts'] = liked_posts
                request.session.modified = True
                post.likes += 1
                post.save()
        return redirect('post_detail', slug=slug)


