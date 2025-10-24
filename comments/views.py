from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from comments.forms import NewCommentForm
from comments.models import Comment
from clone.models import Post
from .models import Notification


# Create your views here.
@login_required
def add_comment(request, post_id):
	"""Handle posting a new comment for a given post.

	Accepts POST with form field 'body'. After saving, redirects back to
	the referring page (or to the home feed if no referrer).
	"""
	post = get_object_or_404(Post, id=post_id)

	if request.method == 'POST':
		form = NewCommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.user = request.user
			comment.post = post
			comment.save()

	# Prefer to return the user to the page they came from
	referer = request.META.get('HTTP_REFERER')
	if referer:
		return redirect(referer)
	return redirect('Home')

def ShowNotification(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')

    context = {
        'notifications': notifications,

    }
    return render(request, 'notifications/notification.html', context)

def DeleteNotification(request, noti_id):
    user = request.user
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('show-notification')
