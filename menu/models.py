from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


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
