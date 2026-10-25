from django import forms

from common.forms import ReadOnlyFormMixin, UniqueNameFormMixin
from menu.models import Allergen, Category, Dish


class DishForm(UniqueNameFormMixin, forms.ModelForm):
    duplicate_message = 'Ястие с име „{name}“ вече съществува.'

    class Meta:
        model = Dish
        exclude = ['created_at', 'updated_at']
        labels = {
            'name': 'Име на ястието',
            'category': 'Категория',
            'allergens': 'Алергени',
            'description': 'Описание',
            'price': 'Цена (€)',
            'weight_grams': 'Грамаж (г)',
            'calories': 'Калории (kcal)',
            'image_url': 'Снимка (URL)',
            'is_vegetarian': 'Вегетарианско',
            'is_available': 'Предлага се',
        }
        help_texts = {
            'allergens': 'Отметни всички алергени, които съдържа ястието.',
            'is_available': 'Махни отметката, ако ястието временно не се приготвя.',
            'image_url': 'Директен линк към снимка (по желание).',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'напр. Боб чорба'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Кратко описание на ястието'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'напр. 2.50'}),
            'weight_grams': forms.NumberInput(attrs={'placeholder': 'напр. 300'}),
            'calories': forms.NumberInput(attrs={'placeholder': 'напр. 450'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'allergens': forms.CheckboxSelectMultiple,
        }
        error_messages = {
            'name': {
                'required': 'Въведи име на ястието.',
            },
            'price': {
                'required': 'Въведи цена.',
                'invalid': 'Въведи валидна цена, например 2.50.',
            },
        }


class DishDeleteForm(ReadOnlyFormMixin, DishForm):
    pass


class CategoryForm(UniqueNameFormMixin, forms.ModelForm):
    duplicate_message = 'Категория с име „{name}“ вече съществува.'

    class Meta:
        model = Category
        fields = ['name', 'position']
        labels = {'name': 'Име на категорията', 'position': 'Поредност'}
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'напр. Супи'}),
        }


class AllergenForm(UniqueNameFormMixin, forms.ModelForm):
    duplicate_message = 'Алерген с име „{name}“ вече съществува.'

    class Meta:
        model = Allergen
        fields = ['number', 'name']
        labels = {'number': 'Номер (1–14)', 'name': 'Алерген'}
        widgets = {
            'number': forms.NumberInput(attrs={'min': 1, 'max': 14, 'placeholder': 'напр. 7'}),
            'name': forms.TextInput(attrs={'placeholder': 'напр. Мляко'}),
        }