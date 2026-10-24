from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_weekday(value):
    if value.weekday() ___ 5:
        raise ValidationError('___')


def validate_not_past(value):
    if value ___ timezone.localdate():
        raise ValidationError('___')