from django.db.models import Sum
from django.utils import timezone
from django.views.generic import TemplateView

from daily_menus.models import DailyMenu
from menu.models import Dish
from orders.models import Order


class HomeView(TemplateView):
    template_name = 'common/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        active_statuses = [Order.Status.NEW, Order.Status.PREPARING, Order.Status.READY]

        context['today_menu'] = DailyMenu.objects.filter(date=today).prefetch_related('dishes').first()
        context['upcoming_menus'] = DailyMenu.objects.filter(date__gt=today)[:3]
        context['dishes_count'] = Dish.objects.count()
        context['orders_today_count'] = Order.objects.filter(daily_menu__date=today).count()
        context['active_orders_count'] = Order.objects.filter(status__in=active_statuses).count()
        context['popular_dishes'] = (
            Dish.objects
            .annotate(total_ordered=Sum('order_items__quantity'))
            .filter(total_ordered__gt=0)
            .order_by('-total_ordered')[:5]
        )
        return context


class AboutView(TemplateView):
    template_name = 'common/about.html'
