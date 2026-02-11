from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v2/', include("users.urls")),
    path('api/v2/', include('products.urls')),
    path('api/v2/', include('payments.urls')),
    path('api/v2/', include('shipments.urls')),
    path('api/v2/', include('orders.urls')),
    path('api/v2/', include('purchases.urls')),
    path('api/v2/', include('carts.urls')),
    path('api/v2/', include('reviews.urls')),
    path('api/v2/', include('blog.urls')),
    path('api/v2/', include('salesreport.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ]
