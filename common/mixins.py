from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect


class SortableListMixin:
    allowed_sorts = ()
    default_sort = None

    def get_ordering(self):
        sort = self.request.GET.get('sort')
        if sort in self.allowed_sorts:
            return sort
        return self.default_sort


class InstanceDeleteFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class ProtectedDeleteMixin:
    protected_message = 'Обектът не може да бъде изтрит, защото се използва.'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message	)
            return redirect(self.object.get_absolute_url())