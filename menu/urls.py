from django.urls import path

from menu import views

app_name = 'menu'

urlpatterns = [
    path('', views.DishListView.as_view(), name='dish-list'),
    path('add/', views.DishCreateView.as_view(), name='dish-create'),
    path('<int:pk>/', views.DishDetailView.as_view(), name='dish-detail'),
    path('<int:pk>/edit/', views.DishUpdateView.as_view(), name='dish-edit'),
    path('<int:pk>/delete/', views.DishDeleteView.as_view(), name='dish-delete'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('allergens/', views.AllergenListView.as_view(), name='allergen-list'),
    path('allergens/add/', views.AllergenCreateView.as_view(), name='allergen-create'),
]