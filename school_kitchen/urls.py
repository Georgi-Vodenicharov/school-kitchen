from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('common.urls')),
    path('menu/', include('menu.urls')),
    path('daily/', include('daily_menus.urls')),
    path('orders/', include('orders.urls')),
]