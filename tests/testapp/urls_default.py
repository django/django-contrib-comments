from django.conf.urls import include, url
from django.contrib.auth.views import login, logout


urlpatterns = [
    url(r'^', include('django_comments.urls')),

    # Provide the auth system login and logout views
    url(r'^accounts/login/$', login, {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', logout),
]
