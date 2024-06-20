# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/preparing/(?P<user_id>\d+)/$', consumers.RedirectConsumer.as_asgi()),
    re_path('ws/orders/', consumers.OrderConsumer.as_asgi()),
]
