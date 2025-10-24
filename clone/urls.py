from django.urls import path
from . import views
from comments.views import add_comment

urlpatterns = [
    path('home', views.home, name="Home"),
    path('newpost', views.NewPost, name='newpost'),
    path('<uuid:post_id>', views.PostDetail, name='post-details'),
    path('<uuid:post_id>/like', views.like, name='like'),
    path('<uuid:post_id>/comment', add_comment, name='add-comment'),

]