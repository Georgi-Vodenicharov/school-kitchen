from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()

STATUS_CLASSES = {
    'new': 'badge-new',
    'preparing': 'badge-preparing',
    'ready': 'badge-ready',
    'served': 'badge-served',
    'cancelled': 'badge-cancelled',
}


@register.filter
def euro(value):
    try:
        amount = Decimal(value)
    except (TypeError, ValueError, InvalidOperation):
        return '—'
    return f'{amount:.2f}'.replace('.', ',') + ' €'


@register.filter
def status_class(value):
    return STATUS_CLASSES.get(value, 'badge-muted')


@register.simple_tag(takes_context=True)
def nav_active(context, namespace):
    request = context.get('request')
    match = getattr(request, 'resolver_match', None)
    if match and match.namespace == namespace:
        return 'active'
    return ''


@register.inclusion_tag('partials/_allergen_badges.html')
def allergen_badges(dish):
    return {'allergens': dish.allergens.all()}