from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from PIL import Image
import uuid
import os
import math


def avatar_file_path(instance, filename):
    """Set the path of the avatar with a random filename"""
    extension = os.path.splitext(filename)[1]
    random_filename = f"{uuid.uuid4().hex}{extension}"
    return os.path.join('avatar_pics/', random_filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to=avatar_file_path)

    def __str__(self):
        return f'{self.user.username} Profile'
    

#Profile receivers
@receiver(post_save, sender=Profile)
def resize_avatar(sender, instance, **kwargs):
    if instance.avatar:
        img = Image.open(instance.avatar.path)
        quality = 20
        img_format = 'JPEG'
        img.save(instance.avatar.path, format=img_format, quality=quality, optimize=True)

@receiver(pre_delete, sender=Profile)
def delete_picture_files(sender, instance, **kwargs):
    # Delete the original file
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)

def picture_file_path(instance, filename):
    """Set the path of the picture with a random filename"""
    extension = os.path.splitext(filename)[1]
    random_filename = f"{uuid.uuid4().hex}{extension}"
    return os.path.join('blog_pictures/', random_filename)

class Category(models.Model):
    
    """Category model"""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):

    """Tag model"""

    tag = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.tag

    def save(self, *args, **kwargs):

        """Set to lowercase the tag"""

        self.tag = self.tag.lower()
        super(Tag, self).save(*args, **kwargs)


class Post(models.Model):

    """Post model"""

    def validate_title_drop(value):
        max_lines = 7
        lines = value.strip().split('\n')
        if len(lines) > max_lines:
            raise ValidationError(f'El contenido no puede exceder de {max_lines} líneas.')

    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=200, unique=True)
    title_drop = RichTextField(null=True, blank=True, validators=[validate_title_drop])
    content = RichTextField(null=True, blank=True)
    main_picture = models.ImageField(upload_to=picture_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=0)
    categories = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    likes = models.PositiveIntegerField(default=0)
    visits = models.PositiveBigIntegerField(default=0, null=True, blank=True)
    estimated_time = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def get_is_visible_display(self):
        return 'Publish' if self.is_visible else 'Draft'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug: 
            self.slug = slugify(self.title)

        word_count = len(self.content.split())
        average_words_per_minute = 230
        estimated_time = (word_count / average_words_per_minute) + 1
        self.estimated_time = math.ceil(estimated_time)

        super(Post, self).save(*args, **kwargs)
        if self.main_picture:
            try:
                self.resize()
            except Exception as e:
                print(f"Error resizing image: {e}")

    def resize(self):
        img = Image.open(self.main_picture.path)
        quality = 30
        img_format = 'JPEG'
        img.save(self.main_picture.path, format=img_format, quality=quality, optimize=True)

    def has_liked(self, request):
        return str(self.id) in request.session.get('liked_posts', [])

    def like(self, request):
        if not self.has_liked(request):
            liked_posts = request.session.get('liked_posts', [])
            liked_posts.append(str(self.id))
            request.session['liked_posts'] = liked_posts
            request.session.modified = True
            self.likes += 1
            self.save(update_fields=['likes'])