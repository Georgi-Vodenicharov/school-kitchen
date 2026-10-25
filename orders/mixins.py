from django.contrib import messages
from django.shortcuts import redirect


class OrderEditableRequiredMixin:
    def get_order(self):
        return self.get_object()

    def dispatch(self, request, *args, **kwargs):
        self.order = self.get_order()
        if not self.order.can_be_edited:
            messages.warning(request, 'Поръчката вече се обработва и не може да се променя.')
            return redirect(self.order.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)