from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', include('django_comments.urls')),

    # Provide the auth system login and logout views
    path('accounts/login/', LoginView.as_view(template_name='login.html')),
    path('accounts/logout/', LogoutView.as_view()),
]
