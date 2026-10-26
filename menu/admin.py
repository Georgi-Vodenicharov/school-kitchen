from django.contrib import admin

from menu.models import Allergen, Category, Dish


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    ordering = ('position',)


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_vegetarian', 'is_available')
    search_fields = ('name',)