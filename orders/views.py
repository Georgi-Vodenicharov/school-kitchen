from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView

from common.mixins import SortableListMixin
from orders.forms import OrderCreateForm, OrderEditForm, OrderItemForm, OrderStatusForm, PaymentForm
from orders.mixins import OrderEditableRequiredMixin
from orders.models import Order, OrderItem


class OrderListView(SortableListMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 15
    allowed_sorts = ('-created_at', 'created_at', 'daily_menu__date', 'class_group')
    default_sort = '-created_at'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('daily_menu').prefetch_related('items')
        params = self.request.GET

        query = params.get('q', '').strip()
        if query:
            queryset = queryset.filter(Q(customer_name__icontains=query) | Q(class_group__icontains=query))

        status = params.get('status', '')
        if status in Order.Status.values:
            queryset = queryset.filter(status=status)

        menu = params.get('menu', '')
        if menu.isdigit():
            queryset = queryset.filter(daily_menu__pk=menu)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.Status.choices
        return context


class OrderDetailView(DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('dish')
        return context


class OrderCreateView(SuccessMessageMixin, CreateView):
    model = Order
    form_class = OrderCreateForm
    template_name = 'orders/order_form.html'

    def get_initial(self):
        initial = super().get_initial()
        menu = self.request.GET.get('menu', '')
        if menu.isdigit():
            initial['daily_menu'] = menu
        return initial

    def get_success_url(self):
        return reverse('orders:item-add', kwargs={'pk': self.object.pk})

    def get_success_message(self, cleaned_data):
        return f'Поръчка № {self.object.pk} беше създадена. Добави ястията.'


class OrderUpdateView(OrderEditableRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Order
    form_class = OrderEditForm
    template_name = 'orders/order_form.html'
    success_message = 'Данните за поръчката са запазени.'


class OrderDeleteView(SuccessMessageMixin, DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:list')
    success_message = 'Поръчката беше изтрита.'


class OrderStatusUpdateView(SuccessMessageMixin, UpdateView):
    model = Order
    form_class = OrderStatusForm
    template_name = 'orders/order_status_form.html'
    success_message = 'Статусът на поръчката беше променен.'


class OrderAdvanceStatusView(View):
    http_method_names = ['post']

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        try:
            order.advance_status()
        except ValueError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, f'Поръчка № {order.pk}: {order.get_status_display()}.')

        next_url = request.POST.get('next', '')
        if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('orders:kitchen')


class OrderItemCreateView(OrderEditableRequiredMixin, SuccessMessageMixin, CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/orderitem_form.html'

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order'] = self.order
        return kwargs

    def form_valid(self, form):
        form.instance.order = self.order
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context

    def get_success_url(self):
        return reverse('orders:item-add', kwargs={'pk': self.order.pk})

    def get_success_message(self, cleaned_data):
        return f'„{self.object.dish.name}“ беше добавено към поръчката.'


class OrderItemDeleteView(OrderEditableRequiredMixin, SuccessMessageMixin, DeleteView):
    model = OrderItem
    template_name = 'orders/orderitem_confirm_delete.html'
    success_message = 'Ястието беше премахнато от поръчката.'

    def get_order(self):
        return self.get_object().order

    def get_success_url(self):
        return reverse('orders:detail', kwargs={'pk': self.order.pk})

class OrderPaymentView(OrderEditableRequiredMixin, FormView):
    form_class = PaymentForm
    template_name = 'orders/order_payment.html'

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context

    def form_valid(self, form):
        try:
            self.order.mark_paid(form.cleaned_data['payment_method'])
        except ValueError as error:
            messages.error(self.request, str(error))
            return redirect(self.order.get_absolute_url())
        messages.success(self.request, f'Поръчка № {self.order.pk} е платена. Приятен апетит!')
        return redirect('orders:receipt', pk=self.order.pk)


class OrderReceiptView(DetailView):
    model = Order
    template_name = 'orders/order_receipt.html'
    context_object_name = 'order'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_paid:
            messages.warning(request, 'Разписка има само за платени поръчки.')
            return redirect(self.object.get_absolute_url())
        return self.render_to_response(self.get_context_data(object=self.object))

class KitchenBoardView(TemplateView):
    template_name = 'orders/kitchen_board.html'
    board_statuses = (Order.Status.NEW, Order.Status.PREPARING, Order.Status.READY)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = (
            Order.objects
            .filter(paid_at__isnull=False)
            .select_related('daily_menu')
            .prefetch_related('items__dish')
            .order_by('daily_menu__date', 'created_at')
        )
        context['columns'] = [
            {'status': status.value, 'label': status.label, 'orders': orders.filter(status=status)}
            for status in self.board_statuses
        ]
        return context