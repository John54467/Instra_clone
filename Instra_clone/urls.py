"""
URL configuration for Instra_clone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from athur.views import register,UserProfile, EditProfile
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clone.urls')),
    path('users/', include('athur.urls')),
    



    # Include chats urls before the catch-all profile patterns so 'message' and other
    # explicit routes are matched instead of being treated as usernames.
    path('', include('chats.urls')),

    #profile urls (explicit per-user routes first)
    path('<username>/profile/edit/', EditProfile, name='user-editprofile'),
    #catch-all username routes
    path('<username>/', UserProfile, name='profile'),
    path('<username>/saved/', UserProfile, name='profilefavourite'),
    path('message/', include('chats.urls')),

]

try:
    # Import here so we only access settings when the environment is configured
    # (manage.py, wsgi/asgi, test runner, etc. will set DJANGO_SETTINGS_MODULE).
    from django.conf import settings
    from django.conf.urls.static import static

    if settings.DEBUG:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
except Exception:
    # Settings aren't configured (e.g., module imported in a standalone script).
    # Skip adding static/media URL patterns to avoid raising ImproperlyConfigured.
    pass


