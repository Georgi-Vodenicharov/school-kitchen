from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from common.models import TimeStampedModel

from django.urls import reverse


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        error_messages={'unique': 'Вече има категория с това име.'},
    )
    position = models.PositiveSmallIntegerField(
        default=1,
        help_text='Поредност в менюто (1 = най-отгоре).',
    )

    class Meta:
        ordering = ['position', 'name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Allergen(models.Model):
    number = models.PositiveSmallIntegerField(
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(14)],
    )
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'{self.number} – {self.name}'


class Dish(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='dishes',
    )
    allergens = models.ManyToManyField(
        Allergen,
        related_name='dishes',
        blank=True,
    )
    description = models.TextField(blank=True, max_length=500)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.10'))],
    )
    weight_grams = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(2000)],
    )
    calories = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(3000)],
    )
    image_url = models.URLField(blank=True)
    is_vegetarian = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name='dish_price_positive',
            ),
        ]

    def __str__(self):
        return self.name

        def get_absolute_url(self):
            return reverse('URL', kwargs={'pk': self.pk})
