from django import forms
from django.utils import timezone

from common.forms import ReadOnlyFormMixin
from common.validators import validate_not_past
from daily_menus.models import DailyMenu
from orders.models import Order, OrderItem


class OrderBaseForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'class_group', 'daily_menu', 'note']
        labels = {
            'customer_name': 'Име и фамилия',
            'class_group': 'Клас',
            'daily_menu': 'Меню за дата',
            'note': 'Бележка към кухнята',
        }
        help_texts = {
            'class_group': 'Например 9А, 10Б, 12В.',
        }
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'напр. Иван Петров'}),
            'class_group': forms.TextInput(attrs={'placeholder': 'напр. 10Б'}),
            'note': forms.TextInput(attrs={'placeholder': 'напр. без лук'}),
        }
        error_messages = {
            'customer_name': {'required': 'Въведи име и фамилия.'},
            'class_group': {'required': 'Въведи клас.'},
            'daily_menu': {'required': 'Избери за кой ден поръчваш.'},
        }

    def clean_customer_name(self):
        name = ' '.join(self.cleaned_data['customer_name'].split())
        if len(name.split()) < 2:
            raise forms.ValidationError('Въведи име и фамилия.')
        return name

    def clean_class_group(self):
        return self.cleaned_data['class_group'].strip().upper()


class OrderCreateForm(OrderBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['daily_menu'].queryset = DailyMenu.objects.filter(date__gte=timezone.localdate())

    def clean_daily_menu(self):
        menu = self.cleaned_data['daily_menu']
        validate_not_past(menu.date)
        return menu


class OrderEditForm(OrderBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['daily_menu'].disabled = True
        self.fields['daily_menu'].help_text = 'Денят не може да се сменя след създаване на поръчката.'


class OrderStatusForm(ReadOnlyFormMixin, forms.ModelForm):
    editable_fields = ('status',)

    class Meta:
        model = Order
        fields = ['customer_name', 'class_group', 'daily_menu', 'status']
        labels = {
            'customer_name': 'Име и фамилия',
            'class_group': 'Клас',
            'daily_menu': 'Меню за дата',
            'status': 'Статус',
        }

    def clean_status(self):
        if self.instance.status in (Order.Status.SERVED, Order.Status.CANCELLED):
            raise forms.ValidationError('Приключена поръчка не може да сменя статуса си.')
        return self.cleaned_data['status']


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity']
        labels = {'dish': 'Ястие', 'quantity': 'Брой порции'}
        help_texts = {'quantity': 'От 1 до 10 порции.'}
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }
        error_messages = {
            'dish': {'required': 'Избери ястие.'},
            'quantity': {'required': 'Въведи брой порции.'},
        }

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order
        if order is not None:
            self.fields['dish'].queryset = order.daily_menu.dishes.filter(is_available=True)

    def clean_dish(self):
        dish = self.cleaned_data['dish']
        if self.order is not None and self.order.items.filter(dish=dish).exists():
            raise forms.ValidationError('Това ястие вече е в поръчката. Премахни го и го добави с новото количество.')
        return dish