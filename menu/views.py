from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from common.mixins import InstanceDeleteFormMixin, ProtectedDeleteMixin, SortableListMixin
from menu.forms import AllergenForm, CategoryForm, DishDeleteForm, DishForm
from menu.models import Allergen, Category, Dish


class DishListView(SortableListMixin, ListView):
    model = Dish
    template_name = 'menu/dish_list.html'
    context_object_name = 'dishes'
    paginate_by = 8
    allowed_sorts = ('name', 'price', '-price', 'calories')
    default_sort = 'name'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').prefetch_related('allergens')
        params = self.request.GET

        query = params.get('q', '').strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

        category = params.get('category', '')
        if category.isdigit():
            queryset = queryset.filter(category__pk=category)

        if params.get('veg') == '1':
            queryset = queryset.filter(is_vegetarian=True)

        without = params.get('without', '')
        if without.isdigit():
            queryset = queryset.exclude(allergens__pk=without)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['allergens'] = Allergen.objects.all()
        return context


class DishDetailView(DetailView):
    model = Dish
    template_name = 'menu/dish_detail.html'
    context_object_name = 'dish'


class DishCreateView(SuccessMessageMixin, CreateView):
    model = Dish
    form_class = DishForm
    template_name = 'menu/dish_form.html'
    success_message = 'Ястието „%(name)s“ беше добавено.'


class DishUpdateView(SuccessMessageMixin, UpdateView):
    model = Dish
    form_class = DishForm
    template_name = 'menu/dish_form.html'
    success_message = 'Промените по „%(name)s“ са запазени.'


class DishDeleteView(InstanceDeleteFormMixin, ProtectedDeleteMixin, SuccessMessageMixin, DeleteView):
    model = Dish
    form_class = DishDeleteForm
    template_name = 'menu/dish_confirm_delete.html'
    success_url = reverse_lazy('menu:dish-list')
    success_message = 'Ястието „%(name)s“ беше изтрито.'
    protected_message = 'Ястието присъства в поръчки и не може да бъде изтрито. Маркирай го като „не се предлага“.'


class CategoryListView(ListView):
    model = Category
    template_name = 'menu/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'menu/category_form.html'
    success_url = reverse_lazy('menu:category-list')
    success_message = 'Категорията „%(name)s“ беше създадена.'


class CategoryUpdateView(SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'menu/category_form.html'
    success_url = reverse_lazy('menu:category-list')
    success_message = 'Категорията „%(name)s“ беше запазена.'


class AllergenListView(ListView):
    model = Allergen
    template_name = 'menu/allergen_list.html'
    context_object_name = 'allergens'


class AllergenCreateView(SuccessMessageMixin, CreateView):
    model = Allergen
    form_class = AllergenForm
    template_name = 'menu/allergen_form.html'
    success_url = reverse_lazy('menu:allergen-list')
    success_message = 'Алергенът „%(name)s“ беше добавен.'
