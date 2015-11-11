from django.conf.urls import include, url
from django.contrib import admin
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
    url(r'^admin/', include(admin_site.urls)),
    url(r'^admin2/', include(admin_site2.urls)),
]
