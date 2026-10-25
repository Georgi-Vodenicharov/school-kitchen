from django.urls import path

from daily_menus import views

app_name = 'daily_menus'

urlpatterns = [
    path('', views.DailyMenuListView.as_view(), name='list'),
    path('add/', views.DailyMenuCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DailyMenuDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.DailyMenuUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DailyMenuDeleteView.as_view(), name='delete'),
]