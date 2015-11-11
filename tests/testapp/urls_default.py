from django.conf.urls import patterns, include
from django.contrib.auth.views import login, logout


urlpatterns = patterns('',
    (r'^', include('django_comments.urls')),

    # Provide the auth system login and logout views
    (r'^accounts/login/$', login, {'template_name': 'login.html'}),
    (r'^accounts/logout/$', logout),
)
