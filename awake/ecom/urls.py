from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecomapp.urls', namespace='sales')),
    path('accounts/', include('useraccounts.urls', namespace='accounts')),
    path('cart/', include('basketapp.urls', namespace='cart')),
    path('ckeditor/', include('django_ckeditor_5.urls')),
    
    
   
]

# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    




