from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'customer_name', 'class_group', 'status', 'paid_at')
    list_filter = ('status', 'payment_method')
    inlines = [OrderItemInline]
