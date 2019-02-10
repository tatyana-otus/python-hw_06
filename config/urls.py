from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.contrib.staticfiles.urls import static
from django.views.generic.base import RedirectView

from .settings import settings


urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('qa:questions'), permanent=True)),
    path('questions/', include('hasker.qa.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('hasker.users.urls')),
    path('api/', include('hasker.api.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
