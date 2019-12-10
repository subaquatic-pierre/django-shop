from django import template
from shop.models import Order, OrderItem, ShopProfile
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        try:
            profile = ShopProfile.objects.get(user__username=user)
            order = Order.objects.get(user=profile, ordered=False)
            order_items = OrderItem.objects.filter(
                order=order, ordered=False)
            if order:
                return order_items.count()
        except ObjectDoesNotExist:
            return 0
