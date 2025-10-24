from chats.views import inbox, directs
from django.urls import path

urlpatterns = [
    path('message/', inbox, name="message"),
    path('directs/<str:username>/', directs, name='directs'),
]