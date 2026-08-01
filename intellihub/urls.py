from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return redirect('accounts:login')

urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('datasets/', include('apps.datasets.urls')),
    path('cleaner/', include('apps.cleaner.urls')),
    path('eda/', include('apps.eda.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('ml-studio/', include('apps.ml_studio.urls')),
    path('dl-studio/', include('apps.dl_studio.urls')),
    path('assistant/', include('apps.assistant.urls')),
    path('scraper/', include('apps.scraper.urls')),
    path('reports/', include('apps.reports.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
