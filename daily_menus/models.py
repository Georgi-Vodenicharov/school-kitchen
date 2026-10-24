from django.db import models
from django.urls import reverse
from django.utils import timezone

from common.models import TimeStampedModel
from common.validators import validate_weekday
from menu.models import Dish


class DailyMenu(TimeStampedModel):
    date = models.DateField(
        unique=True,
        validators=[validate_weekday],
        error_messages={'unique': 'Вече има меню за тази дата.'},
    )
    title = models.CharField(max_length=80, blank=True)
    dishes = models.ManyToManyField(
        Dish,
        related_name='daily_menus',
    )
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.date:%d.%m.%Y} – {self.title or "Обедно меню"}'

    def get_absolute_url(self):
        return reverse('daily_menus:detail', kwargs={'pk': self.pk})

    @property
    def is_today(self):
        return self.date == timezone.localdate()

    @property
    def is_past(self):
        return self.date < timezone.localdate()