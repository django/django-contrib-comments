from django.contrib import admin
from django.urls import path

from django_comments.admin import CommentsAdmin
from django_comments.models import Comment

# Make a new AdminSite to avoid picking up the deliberately broken admin
# modules in other tests.
admin_site = admin.AdminSite()
admin_site.register(Comment, CommentsAdmin)

# To demonstrate proper functionality even when ``delete_selected`` is removed.
admin_site2 = admin.AdminSite()
admin_site2.disable_action('delete_selected')
admin_site2.register(Comment, CommentsAdmin)

urlpatterns = [
    path('admin/', admin_site.urls),
    path('admin2/', admin_site2.urls),
]
