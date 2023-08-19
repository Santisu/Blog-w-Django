from django.shortcuts import redirect, render
from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
from .forms import PostForm, CategoryForm, TagForm


class BlogView(View):
    template = 'blog_main.html'

    def get(self, request):
        query = request.GET.get('q')
        categories = Category.objects.all().order_by('name')
        tags = Tag.objects.all()
        if query:
            main_post = None
            posts = Post.objects.filter(
                title__icontains=query, is_visible=1).order_by('-created_at')
        else:
            main_post = Post.objects.filter(
                is_visible=1).order_by('-created_at').first()
            posts = Post.objects.filter(is_visible=1).exclude(
                id=main_post.id).order_by('-created_at')

        context = {'main_post': main_post,
                   'posts': posts,
                   'categories': categories,
                   'tags': tags}
        return render(request, self.template, context)


class TagSearchView(View):
    template_name = 'blog_main.html'

    def get(self, request, tag):
        posts = Post.objects.filter(
            tags__tag__iexact=tag, is_visible=1).order_by('-created_at')
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
        posts = Post.objects.filter(
            categories=category, is_visible=1).order_by('-created_at')
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

        post = get_object_or_404(Post, slug=slug, is_visible=1)
        related_posts = Post.objects.filter(
            categories=post.categories, is_visible=1).exclude(id=post.id).order_by('-visits')[:4]

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
        # Verifys if current session has liked the post, if not adds +1 to likes, works together with the templatetag 'has_liked'
        if submit_action == 'like_submit':
            liked_posts = request.session.get('liked_posts', [])
            if str(post.id) not in liked_posts:
                liked_posts.append(str(post.id))
                request.session['liked_posts'] = liked_posts
                request.session.modified = True
                post.likes += 1
                post.save()
        return redirect('post_detail', slug=slug)


class PostCreationView(View):

    """
    Creates/edit posts, tags and categories
    """
    template_name = 'blog_post_creation.html'
    post_form = PostForm
    tag_form = TagForm
    category_form = CategoryForm

    def get(self, request, *args, **kwargs):
        """
        Send the forms for creation of posts, categories and tags.
        If it recibes a post's slug, it loads it for edition
        """
        categories = Category.objects.all()
        tags = Tag.objects.all()
        slug = self.kwargs.get('slug')
        if slug:
            post = get_object_or_404(Post, slug=slug)
            initial_data = {
                'title': post.title,
                'title_drop': post.title_drop,
                'content': post.content,
                'main_picture': post.main_picture,
                'categories': post.categories,
                'tags': post.tags.all(),
                'is_visible': post.is_visible,
            }
            post_form = self.post_form(initial=initial_data)
        else:
            post_form = self.post_form()
        context = {
            'post_form': post_form,
            'category_form': self.category_form(),
            'tag_form': self.tag_form(),
            'categories': categories,
            'tags': tags,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        submit_action = request.POST.get('submit_action')
        error = None
        post_error = False
        slug = self.kwargs.get('slug')

        if submit_action == 'post_submit':
            if slug:
                post = get_object_or_404(Post, slug=slug)
                post_form = self.post_form(
                    request.POST, request.FILES, instance=post)
            else:
                post_form = self.post_form(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.author = request.user
                post.save()
                post.tags.set(post_form.cleaned_data['tags'])
                slug = post.slug
                return redirect('post_detail', slug=slug)
            else:
                error = post_form.errors
                post_error = True

        elif submit_action == 'category_submit':
            category_form = self.category_form(request.POST)
            if category_form.is_valid():
                category = category_form.save()
                return redirect('post_creation')
            else:
                error = category_form.errors

        elif submit_action == 'tag_submit':
            tag_form = self.tag_form(request.POST)
            if tag_form.is_valid():
                tag = tag_form.save()
                return redirect('post_creation')
            else:
                error = tag_form.errors

        elif submit_action == 'delete_tag':
            tag_id = request.POST.get('tag_id')
            if tag_id:
                try:
                    tag = Tag.objects.get(id=tag_id)
                    tag.delete()
                    return redirect('post_creation')
                except Tag.DoesNotExist:
                    error = "El tag no existe o ya ha sido eliminado."

        elif submit_action == 'delete_category':
            category_id = request.POST.get('category_id')
            try:
                category = Category.objects.get(id=category_id)
                category.delete()
            except Category.DoesNotExist:
                error = "Categoría no encontrada."

        if post_error:
            post_form = self.post_form(request.POST, request.FILES)
        else:
            post_form = self.post_form()

        category_form = self.category_form()
        tag_form = self.tag_form()

        categories = Category.objects.all()
        tags = Tag.objects.all()
        context = {
            'post_form': post_form,
            'category_form': category_form,
            'tag_form': tag_form,
            'categories': categories,
            'tags': tags,
            'errors': error,
        }

        return render(request, self.template_name, context)
