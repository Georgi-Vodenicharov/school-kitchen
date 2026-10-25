from django.urls import path

from orders import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('add/', views.OrderCreateView.as_view(), name='create'),
    path('kitchen/', views.KitchenBoardView.as_view(), name='kitchen'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.OrderUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='delete'),
    path('<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='status'),
    path('<int:pk>/advance/', views.OrderAdvanceStatusView.as_view(), name='advance'),
    path('<int:pk>/items/add/', views.OrderItemCreateView.as_view(), name='item-add'),
    path('items/<int:pk>/delete/', views.OrderItemDeleteView.as_view(), name='item-delete'),
]