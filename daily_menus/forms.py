from django import forms
from django.db.models import Q

from common.forms import ReadOnlyFormMixin
from common.validators import validate_not_past
from daily_menus.models import DailyMenu
from menu.models import Dish


class DailyMenuForm(forms.ModelForm):
    class Meta:
        model = DailyMenu
        fields = ['date', 'title', 'dishes', 'note']
        labels = {
            'date': 'Дата',
            'title': 'Заглавие',
            'dishes': 'Ястия в менюто',
            'note': 'Бележка',
        }
        help_texts = {
            'date': 'Само учебен ден (понеделник – петък).',
            'title': 'По желание, напр. „Есенно меню“.',
        }
        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'Обедно меню'}),
            'dishes': forms.CheckboxSelectMultiple,
            'note': forms.TextInput(attrs={'placeholder': 'напр. Днес има и плодове за десерт'}),
        }
        error_messages = {
            'date': {'required': 'Избери дата.', 'invalid': 'Въведи валидна дата.'},
            'dishes': {'required': 'Избери поне едно ястие за менюто.'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available = Q(is_available=True)
        if self.instance.pk:
            available |= Q(pk__in=self.instance.dishes.all())
        self.fields['dishes'].queryset = Dish.objects.filter(available).distinct()

    def clean_date(self):
        date = self.cleaned_data['date']
        if self.instance.pk is None:
            validate_not_past(date)
        return date


class DailyMenuDeleteForm(ReadOnlyFormMixin, DailyMenuForm):
    pass