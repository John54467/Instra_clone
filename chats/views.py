from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from chats.models import Message
from django.contrib.auth.models import User


@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=request.user)
    active_direct = None
    directs = None
    

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0
    context = {
        'messages': messages,
        'active_direct': active_direct,
    }
    return render(request, 'message.html', context)


@login_required
def directs(request, username):
    # Load the target user and the conversation with the requesting user
    other = get_object_or_404(User, username=username)
    # If POST, create a new message (fallback for non-WebSocket clients)
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            Message.sender_message(request.user, other, body)
        return redirect('directs', username=username)
    # Mark directs between request.user and other as read for the current user view
    directs_qs = Message.objects.filter(user=request.user, reciepient=other).order_by('date')
    directs_qs.update(is_read=True)

    # Build messages list for sidebar using the existing helper
    messages = Message.get_message(user=request.user)
    active_direct = other.username

    context = {
        'messages': messages,
        'active_direct': active_direct,
        'directs': directs_qs,
        'other_user': other,
    }
    return render(request, 'message.html', context)

def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == "POST":
        to_user = User.objects.get(username=to_user_username)
        Message.sender_message(from_user, to_user, body)
        return redirect('message')