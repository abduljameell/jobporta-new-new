from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ✅ Admin Panel Route
    path('admin/', admin.site.urls),  

    # ✅ Include URLs from the app
    path('', include('myapp.urls')),  

    # ✅ Authentication Routes (if needed)
    path('accounts/', include('django.contrib.auth.urls')),  # For login, logout, password reset, etc.
]

# ✅ Serve static and media files only in development mode
if settings.DEBUG:
    # ✅ Serve media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # ✅ Serve static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
