try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url
from django.conf.urls import include
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    url(r'^', include('django_comments.urls')),

    # Provide the auth system login and logout views
    url(r'^accounts/login/$', LoginView.as_view(template_name='login.html')),
    url(r'^accounts/logout/$', LogoutView.as_view()),
]
