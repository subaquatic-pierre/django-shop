import csv
import io
import random
import string
import os


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.core.files import File

from .forms import CouponForm
from .models import (Brand, Category, Color, Coupon, Item, Label, Order,
                     OrderItem, ShopProfile, Size, ItemInfo)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False

    return valid


def generate_ref_code():
    # printing letters
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(16))


@login_required
def add_to_cart(request, slug):
    try:
        profile = ShopProfile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.info(request, 'Shop profile does not exist')
        return redirect('shop:home')

    item = get_object_or_404(Item, slug=slug)
    order, order_created = Order.objects.get_or_create(
        user=profile, ordered=False)
    order_item, order_item_created = OrderItem.objects.get_or_create(
        item=item,
        order=order,
        ordered=False
    )
    if order_created:
        order.ref_code = generate_ref_code()
        order.save()
        order_item.order = order
        order_item.save()
        profile.current_order = order
        profile.save()
        messages.info(request, 'The item has been added to your cart')
        return redirect('shop:product', slug=slug)
    else:
        if not order_item_created:
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'Your item has been updated in the cart')
            return redirect('shop:order_summary')
        else:
            order_item.order = order
            messages.info(request, 'The item has been added to your cart')
            return redirect('shop:product', slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    try:
        order = Order.objects.get(user=request.user.shopprofile, ordered=False)
    except ObjectDoesNotExist:
        messages.info(request, 'You do not have any active orders')
        return redirect('shop:order_summary')
    try:
        order_item = OrderItem.objects.filter(
            order=order, item__slug=item.slug, ordered=False).delete()
        messages.info(request, 'This item was removed from your cart')
        return redirect('shop:order_summary')
    except ObjectDoesNotExist:
        messages.info(request, 'This item was not in your cart')
        return redirect('shop:order_summary')


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    try:
        order = Order.objects.get(user=request.user.shopprofile, ordered=False)
    except ObjectDoesNotExist:
        messages.info(request, 'You do not have any active orders')
        return redirect('shop:order_summary')
    try:
        order_item = OrderItem.objects.get(
            order=order, item__slug=item.slug, ordered=False)
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order_item.delete()
        messages.info(request, 'Your item has been updated in the cart')
        return redirect('shop:order_summary')
    except ObjectDoesNotExist:
        messages.info(request, 'This item was not in your cart')
        return redirect('shop:order_summary')


@login_required
def delete_cart(request):
    profile = ShopProfile.objects.get(user=request.user)
    order = Order.objects.get(user=profile, ordered=False).delete()
    profile.current_order = None
    profile.save()
    messages.info(request, 'Your cart has been deleted')
    return redirect('shop:home')


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        return None


@login_required
def add_coupon(request):
    form = CouponForm(request.POST or None)
    if form.is_valid():
        code = form.cleaned_data.get('code')
        coupon = get_coupon(request, code)
        # TODO: Check user has not already used coupon
        # TODO: Check coupon does not exceed total order amount
        if not coupon:
            messages.info(request, 'Not a valid coupon')
            return redirect('shop:checkout')
        try:
            profile = ShopProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            messages.info(request, 'You do not have a shop profile')
            return redirect('shop:checkout')
            # Check user has current order
        try:
            order = Order.objects.get(user=profile, ordered=False)
            order.coupon = coupon
            order.save()
            messages.info(request, 'Coupon has been successfuly added')
            return redirect('shop:checkout')
        except ObjectDoesNotExist:
            messages.info(request, 'You do not have an active order')
            return redirect('shop:checkout')

    messages.info(request, 'Invalid form input')
    return redirect('shop:home')


def upload_shop_data(file):

    data_set = file.read().decode('utf-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    reader = csv.reader(io_string, delimiter=',', quotechar="|")
    # TODO: Improve column checking programatically in upload_shop_data function
    for line in reader:
        if not line[8] == '':
            category, created = Category.objects.get_or_create(title=line[8])
        if not line[4] == '':
            brand, created = Brand.objects.get_or_create(title=line[4])

        price = line[2]

        # Check discount price is not empty
        if not line[9] == '':
            discount_price = line[9]

        # Check price is not empty
        if price == '':
            price = 0
        if discount_price == '':
            discount_price = None

        item, created = Item.objects.get_or_create(
            sku=line[0],
        )

        # if not line[5] == '':
        #     i = File(open('/home/pierre/Downloads/default.jpg', 'rb'))
        #     item.image.save('default.jpg', i, save=True)
        item.title = line[1]
        item.price = price
        item.stock_count = line[3]
        item.brand = brand
        item.slug = line[6]
        if not line[7] == '':
            item.description = line[7]
        item.category = category
        item.discount_price = discount_price
        if not line[10] == '':
            size, created = Size.objects.get_or_create(title=line[10])
            item.size = size
        if not line[11] == '':
            color, created = Color.objects.get_or_create(title=line[11])
            item.color = color

        if not line[12] == '':
            label, created = Label.objects.get_or_create(title=line[12])
            label.color = line[13]
            label.save()
            item.label = label

        # Get item info
        cursor = 14
        for i in range(3):
            item_info_title = line[cursor]
            item_info_heading = line[cursor+1]
            item_info_text = line[cursor+2]
            item_info, created = ItemInfo.objects.get_or_create(
                title=item_info_title)
            item_info.heading = item_info_heading
            item_info.text = item_info_text
            item_info.save()
            item.item_info.add(item_info)
            cursor += 3

        item.save()

    return 1
