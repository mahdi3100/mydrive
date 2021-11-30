from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("getDir", views.getDir, name="getDir"),
    path("setDir", views.setDir, name="setDir"),
    path("setFiles", views.setFiles, name="setFiles"),
    path("download", views.download, name="download"),
    path("setprivercy", views.setprivercy, name="setprivercy"),
    path("search", views.search, name="search"),
    path("settingsUser", views.settingsUser, name="settingsUser")




    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
