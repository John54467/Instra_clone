from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post,Follow, Stream, Likes
from .forms import NewPostform
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import F
from django.db import transaction
from comments.forms import NewCommentForm




def home(request):
    user = request.user
    
    if user.is_authenticated:
        posts = Stream.objects.filter(user=user)
    else:
        posts = Stream.objects.none()
    group_ids = []

    
    for post in posts:
        group_ids.append(post.post_id)
        
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
 
    context = {
        'post_items': post_items,
        'post_items_count': post_items.count(),
        'comment_form': NewCommentForm(),
    }
    return render(request, 'index.html', context)

def NewPost(request):
    user = request.user
    if request.method == 'POST':
        form = NewPostform(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('Home')
    else:
        form = NewPostform()
    return render(request, "newpost.html", {'form': form})


def PostDetail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    context = {
        'post': post,
    }

    return render(request, 'postdetail.html', context)


@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).count()

    if not liked:
        Likes.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
        
    post.likes = current_likes
    post.save()

    # Redirect back to the post detail view
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))





  

