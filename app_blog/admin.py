from django.contrib import admin
from .models import Category, Tag, Post, Profile

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'name': ('name',)}

class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    prepopulated_fields = {'tag': ('tag',)}

class TagInline(admin.TabularInline):
    model = Post.tags.through
    extra = 1

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'status', 'likes')
    list_filter = ('status', 'created_at', 'author', 'categories', 'tags')
    search_fields = ('title', 'content')
    readonly_fields = ('slug', 'visits', 'likes', 'estimated_time')
    exclude = ('tags',)
    inlines = [TagInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile)
