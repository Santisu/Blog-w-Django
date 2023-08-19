from django import forms
from .models import Post, Category, Tag
from ckeditor.widgets import CKEditorWidget

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)
        labels = {
            'name': 'Nueva Categoría',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'label_class': 'form-label'})}
        

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        labels = {
            'tag': 'Nuevo Tag',
        }
        fields = ('tag',)
        widgets = {
            'tag': forms.TextInput(attrs={'class': 'form-control'})}
        

class PostForm(forms.ModelForm):
    categories = forms.ModelChoiceField(queryset=Category.objects.all(), label='Categoría', widget=forms.Select(attrs={'class': 'form-select tag-select'}))

    class Meta:
        model = Post
        exclude = ('slug', 'author', 'created_at', 'updated_at', 'likes', 'visits', 'estimated_time')
        labels = {
            'title': 'Título',
            'title_drop': 'Bajada de título (Max. 7 lineas)',
            'content': 'Contenido',
            'main_picture': 'Imágen principal',
            'categories': 'Categorías',
            'tags': 'Tags',
            'is_visible': 'Visible',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'main_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select tag-select'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
