from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login
from clone.models import Post, Follow, Stream
from athur.models import Profile
from .forms import EditProfileForm,UserRegisterForm
from django.urls import resolve



def UserProfile(request, username):
    # Ensure a Profile exists for the visiting user only if they're authenticated.
    if request.user.is_authenticated:
        Profile.objects.get_or_create(user=request.user)
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
    posts = Post.objects.filter(user=user).order_by('-posted')

    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts = profile.favourite.all()
    
    # Profile Stats
    posts_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    # If the visitor is anonymous, they cannot follow — avoid filtering by AnonymousUser
    if request.user.is_authenticated:
        follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
    else:
        follow_status = False


    context = {
        'posts': posts,
        'profile':profile,
        'posts_count':posts_count,
        'following_count':following_count,
        'followers_count':followers_count,
        'follow_status':follow_status,
    }
    return render(request, 'profile.html', context)

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            # Profile.get_or_create(user=request.user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hurray your account was created!!')

            # Automatically Log In The User
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],)
            login(request, new_user)
            return redirect('Home')
    # If the visitor is already authenticated, redirect to index
    if request.user.is_authenticated:
        return redirect('Home')

    # For GET requests, show blank form
    form = UserRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


def EditProfile(request, username=None):
    # Allow access to /<username>/profile/edit/ or the generic /users/profile/edit/
    if not request.user.is_authenticated:
        return redirect('sign-in')

    # If username provided in the URL, load that user's profile; otherwise use current user
    if username:
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        # Only allow the profile owner to edit their profile
        if profile.user != request.user:
            messages.warning(request, 'You are not allowed to edit this profile.')
            return redirect('profile', username)
    else:
        profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Copy cleaned data into profile fields and save
            profile.image = form.cleaned_data.get('image')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.bio = form.cleaned_data.get('bio')
            profile.save()
            return redirect('profile', profile.user.username)
    else:
        form = EditProfileForm(instance=profile)

    context = {
        'form': form,
    }
    # Template file is `edit_profile.html` in templates directory
    return render(request, 'edit_profile.html', context)