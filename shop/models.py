import random
import string

from django.apps import apps
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify


# TODO: Created date for OrderItem, Payment, Refund, Order


class ShopProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    current_order = models.ForeignKey(
        'Order', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)

    # Coupons
    redeemend_coupons = models.ManyToManyField('Coupon', blank=True)

    # Payment credentials
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.user}'


class Address(models.Model):

    ADDRESS_CHOICES = (
        ('B', 'Billing'),
        ('S', 'Shipping'),
    )

    user = models.ForeignKey(
        'ShopProfile', to_field='user', on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.address_line_1}'


class Order(models.Model):
    user = models.ForeignKey(
        'ShopProfile', to_field='user', on_delete=models.CASCADE)
    ref_code = models.CharField(
        max_length=30, unique=True)
    ordered = models.BooleanField(default=False)
    start_date = models.DateField(auto_now=True)
    ordered_date = models.DateField(null=True, blank=True)
    billing_address = models.ForeignKey(
        'Address', related_name='order_billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='order_shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    on_delivery = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Add billing address
    (Failed checkout)
    3. Payment
    (Supply chain proccess, contact supplier, courier, ect.)
    4. Being delivered
    5. Been received
    6. Refunds
    '''

    def get_total(self):
        total = 0
        order_items = OrderItem.objects.filter(
            order=self, ordered=False)
        for item in order_items:
            total += item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return round(total, 2)

    def __str__(self):
        return f'{self.user} - start date:{self.start_date}'


class Payment(models.Model):

    PAYMENT_OPTION_CHOICES = (
        ('stripe', 'Stripe'),
        ('paypal', 'Paypal'),
        ('cash', 'Cash'),
    )

    user = models.ForeignKey(
        'ShopProfile', to_field='user', on_delete=models.CASCADE)
    payment_option = models.CharField(
        max_length=20, choices=PAYMENT_OPTION_CHOICES)
    stipe_id_code = models.CharField(max_length=50, blank=True, null=True)
    paypal_id_code = models.CharField(max_length=50, blank=True, null=True)
    amount = models.FloatField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    ref_code = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.user} - amount:{self.amount}'


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    amount = models.FloatField()

    def __str__(self):
        return f'{self.code}'


class Refund(models.Model):
    user = models.ForeignKey(
        'ShopProfile', to_field='user', on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    # Set refund ref code to say refund infront in views.py
    ref_code = models.CharField(max_length=30, unique=True)
    username = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.pk}'


# Item models

# TODO: Remove single Image class, add image to Item class

class Item(models.Model):
    # required fields
    sku = models.CharField(max_length=60, primary_key=True)
    title = models.CharField(max_length=100)
    price = models.FloatField(null=True, blank=True)
    stock_count = models.IntegerField(null=True, blank=True)
    brand = models.ForeignKey(
        'Brand', on_delete=models.SET_DEFAULT, default=1)
    image = models.ImageField(default='default.jpg')
    slug = models.SlugField(default='', editable=False,
                            max_length=100)
    description = models.TextField(
        default='Short Description here, all the items are the most amazing items one can find. Please take a minute to really appreciate everything around you. Without pain there could be no pleasure. Enjoy the pain for the pain carries the pleasure')
    category = models.ForeignKey(
        'Category', default=1, on_delete=models.SET_DEFAULT)

    # optional fields
    discount_price = models.FloatField(null=True, blank=True)
    size = models.ForeignKey('Size',
                             on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey('Color',
                              on_delete=models.SET_NULL, null=True, blank=True)
    label = models.ForeignKey(
        'Label', on_delete=models.SET_NULL, null=True, blank=True)
    item_info = models.ManyToManyField('ItemInfo', blank=True)

    def get_absolute_url(self):
        return reverse('shop:product', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('shop:add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('shop:remove_from_cart', kwargs={'slug': self.slug})

    # Make slug when saving item
    def save(self, *args, **kwargs):
        sku = self.sku
        self.slug = slugify(sku, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        'Order', related_name='item', on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def get_total_price(self):
        return round(self.quantity * self.item.price, 2)

    def get_total_discount_price(self):
        return round(self.quantity * self.item.discount_price, 2)

    def get_amount_saved(self):
        return round(self.get_total_price() - self.get_total_discount_price(), 2)

    def get_final_price(self):
        if self.item.discount_price:
            return round(self.get_total_discount_price(), 2)
        return round(self.get_total_price(), 2)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(default='', editable=False,
                            max_length=100)
    image = models.ImageField(default='default_category.jpg')

    # Make slug when saving item

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'{self.title}'


class Size(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.title}'


class Color(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.title}'


class Brand(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.title}'


class Label(models.Model):
    title = models.CharField(max_length=20)
    color = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.title}'


class ItemInfo(models.Model):
    title = models.CharField(max_length=255, primary_key=True)
    heading = models.CharField(max_length=255)
    text = models.TextField(default='This is default info on the item')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name_plural = 'Item Info'
