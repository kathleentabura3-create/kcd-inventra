from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect  # <-- Import redirect

urlpatterns = [
    path('', lambda request: redirect('product_list')),  # <-- Add this line to handle the empty homepage path
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)