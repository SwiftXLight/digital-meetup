from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from event import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.landing, name="landing"),
    path("register/", views.register, name="register"),
    path("register/success/", views.registration_success, name="registration_success"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
