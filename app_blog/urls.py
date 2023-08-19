from django.urls import path
from .views import BlogView, CategorySearchView, PostCreationView, PostDetailView, TagSearchView


urlpatterns = [
    path('', BlogView.as_view(), name="blog"),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('tag/<str:tag>/', TagSearchView.as_view(), name='tag_search'),
    path('category/<int:category_id>/', CategorySearchView.as_view(), name='category_search'),
    path('new-post/', PostCreationView.as_view(), name='post_creation'),
    path('post/edit/<slug:slug>/', PostCreationView.as_view(), name='post_edit'),

]