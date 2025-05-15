from django.views.static import serve
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include("users.urls")),
    path('api/v1/', include('products.urls')),
    path('api/v1/', include('payments.urls')),
    path('api/v1/', include('shipments.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('purchases.urls')),
    path('api/v1/', include('carts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]