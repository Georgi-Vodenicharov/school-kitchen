from django.contrib import admin

from daily_menus.models import DailyMenu


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ('date', 'title')
    filter_horizontal = ('dishes',)
