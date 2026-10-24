from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.urls import reverse

from common.models import TimeStampedModel
from daily_menus.models import DailyMenu
from menu.models import Dish


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = 'new', 'Нова'
        PREPARING = 'preparing', 'Приготвя се'
        READY = 'ready', 'Готова'
        SERVED = 'served', 'Получена'
        CANCELLED = 'cancelled', 'Отказана'

    NEXT_STATUS = {
        'new': 'preparing',
        'preparing': 'ready',
        'ready': 'served',
    }

    customer_name = models.CharField(
        max_length=60,
        validators=[RegexValidator(
            r'^[A-Za-zА-Яа-я\s-]+$',
            'Името може да съдържа само букви, интервали и тире.',
        )],
    )
    class_group = models.CharField(
        max_length=3,
        validators=[RegexValidator(
            r'^(8|9|10|11|12)[А-Е]$',
            'Въведи клас във формат 8А–12Е',
        )],
    )
    daily_menu = models.ForeignKey(
        DailyMenu,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NEW,
    )
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Поръчка № {self.pk}'

    def get_absolute_url(self):
        return reverse('orders:detail', kwargs={'pk': self.pk})

    @property
    def total(self):
        return sum((item.line_total for item in self.items.all()), Decimal('0'))

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def can_be_edited(self):
        return self.status == self.Status.NEW

    @property
    def next_status_label(self):
        next_status = self.NEXT_STATUS.get(self.status)
        if next_status is None:
            return None
        return self.Status(next_status).label

    def advance_status(self):
        next_status = self.NEXT_STATUS.get(self.status)
        if next_status is None:
            raise ValueError('Поръчката няма следващ етап.')
        self.status = next_status
        self.save(update_fields=['status', 'updated_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'dish'],
                name='unique_dish_per_order',
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name='order_item_quantity_positive',
            ),
        ]

    def __str__(self):
        return f'{self.quantity} × {self.dish}'

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.dish.price
        super().save(*args, **kwargs)

    @property
    def line_total(self):
        if self.unit_price is None:
            return Decimal('0')
        return self.unit_price * self.quantity