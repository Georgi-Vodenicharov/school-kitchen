from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from common.mixins import InstanceDeleteFormMixin, ProtectedDeleteMixin
from daily_menus.forms import DailyMenuDeleteForm, DailyMenuForm
from daily_menus.models import DailyMenu


class DailyMenuListView(ListView):
    model = DailyMenu
    template_name = 'daily_menus/dailymenu_list.html'
    context_object_name = 'menus'

    def get_queryset(self):
        today = timezone.localdate()
        queryset = super().get_queryset().prefetch_related('dishes')
        when = self.request.GET.get('when', 'upcoming')
        if when == 'past':
            return queryset.filter(date__lt=today).order_by('-date')
        if when == 'all':
            return queryset.order_by('-date')
        return queryset.filter(date__gte=today).order_by('date')


class DailyMenuDetailView(DetailView):
    model = DailyMenu
    template_name = 'daily_menus/dailymenu_detail.html'
    context_object_name = 'menu'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_dishes'] = (
            self.object.dishes
            .select_related('category')
            .prefetch_related('allergens')
            .order_by('category__position', 'category__name', 'name')
        )
        return context


class DailyMenuCreateView(SuccessMessageMixin, CreateView):
    model = DailyMenu
    form_class = DailyMenuForm
    template_name = 'daily_menus/dailymenu_form.html'

    def get_success_message(self, cleaned_data):
        return f'Менюто за {self.object.date:%d.%m.%Y} беше публикувано.'


class DailyMenuUpdateView(SuccessMessageMixin, UpdateView):
    model = DailyMenu
    form_class = DailyMenuForm
    template_name = 'daily_menus/dailymenu_form.html'

    def get_success_message(self, cleaned_data):
        return f'Менюто за {self.object.date:%d.%m.%Y} беше запазено.'


class DailyMenuDeleteView(InstanceDeleteFormMixin, ProtectedDeleteMixin, SuccessMessageMixin, DeleteView):
    model = DailyMenu
    form_class = DailyMenuDeleteForm
    template_name = 'daily_menus/dailymenu_confirm_delete.html'
    success_url = reverse_lazy('daily_menus:list')
    protected_message = 'По това меню има поръчки и то не може да бъде изтрито.'

    def get_success_message(self, cleaned_data):
        return f'Менюто за {self.object.date:%d.%m.%Y} беше изтрито.'