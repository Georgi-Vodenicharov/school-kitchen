from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_weekday(value):
    if value.weekday() >= 5:
        raise ValidationError('Кухнята не работи в събота и неделя')


def validate_not_past(value):
    if value < timezone.localdate():
        raise ValidationError('Датата не може да бъде в миналото')