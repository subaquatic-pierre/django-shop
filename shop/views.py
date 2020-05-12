# import random
# import string
import csv
from datetime import datetime

import stripe
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView


from .forms import (CheckoutForm, CouponForm, PaymentForm, RefundForm,
                    ShopItemsUploadForm)
from .models import (Address, Category, Coupon, Item, Order, OrderItem,
                     Payment, Refund, ShopProfile)
from .utils import (add_to_cart, is_valid_form,
                    remove_from_cart, remove_single_item_from_cart, upload_shop_data)

stripe.api_key = settings.STRIPE_SECRET_KEY

# TODO: Create User Profile view, prepopulate forms with all user data
# TODO: Search functionality for shop items
# TODO: Fix Pagination to include page numbers either side of current page on Home and category pages
# TODO: Fix select category links to become active when on that page
# TODO: Add link to item page on item in cart
# TODO: Create request refund functionality


class HomeView(ListView):
    model = Item
    template_name = 'shop/home.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['hero_header'] = 'Amazing Life'
        return context


class ProductView(DetailView):
    model = Item
    template_name = 'shop/product.html'
    context_object_name = 'item'


class CategoryListView(ListView):
    model = Category
    template_name = "shop/category_list.html"
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_header'] = 'Categories'
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = "shop/category_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['items'] = Item.objects.filter(
            category=category)
        context['categories'] = Category.objects.all()
        context['hero_header'] = category.title
        return context


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        # Check profile exists
        try:
            profile = ShopProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            messages.info(request, 'You do not have a shop profile')
            return redirect('shop:home')
        # Check order exists
        try:
            order = Order.objects.get(user=profile, ordered=False)
            form = CheckoutForm()
            order_items = OrderItem.objects.filter(order=order, ordered=False)
            context = {
                'order': order,
                'form': form,
                'order_items': order_items,
                'coupon_form': CouponForm()
            }

            if profile.shipping_address:
                context.update(
                    {'default_shipping_address': profile.shipping_address})

            if profile.billing_address:
                context.update(
                    {'default_billing_address': profile.billing_address})

            return render(request, 'shop/checkout.html', context)

        except ObjectDoesNotExist:
            messages.info(request, 'You do not have an active order')
            return redirect('shop:home')

    # TODO: Set logic when changing address to current in CheckoutView POST method
    # TODO: Fix order billing/shipping address when order is made
    def post(self, request, *args, **kwargs):
        try:
            # Get user profile
            profile = ShopProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            messages.info(request, 'No shop profile exists')
            return redirect('shop:home')
        try:
            order = Order.objects.get(user=profile, ordered=False)

            # Get form info, add info to order
            form = CheckoutForm(request.POST or None)
            if form.is_valid():
                # Check if using default shipping and default billing address from form
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                # Shipping Address Logic
                if use_default_shipping:
                    if profile.shipping_address:
                        order_shipping_address = profile.shipping_address
                        order.shipping_address = order_shipping_address
                        order.save()
                    else:
                        messages.info(
                            request, 'No default shipping address available')
                        return redirect('shop:checkout')
                else:
                    # Make new shipping address for order
                    shipping_address_1 = form.cleaned_data.get(
                        'shipping_address_1')
                    shipping_address_2 = form.cleaned_data.get(
                        'shipping_address_2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip_code = form.cleaned_data.get(
                        'shipping_zip_code')

                    if is_valid_form([shipping_address_1, shipping_country, shipping_zip_code]):
                        order_shipping_address = Address(
                            user=profile,
                            address_line_1=shipping_address_1,
                            address_line_2=shipping_address_2,
                            country=shipping_country,
                            zip_code=shipping_zip_code,
                            address_type='S'
                        )
                        order_shipping_address.save()
                        order.shipping_address = order_shipping_address
                        order.save()

                        # set default shipping if user checked set default in form
                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            profile.shipping_address = order_shipping_address
                    else:
                        messages.info(
                            request, 'Please fill in the required shipping address fields')
                        return redirect('shop:checkout')
                if same_billing_address and use_default_shipping:
                    order_billing_address = Address(
                        user=profile,
                        address_line_1=profile.shipping_address.address_line_1,
                        address_line_2=profile.shipping_address.address_line_2,
                        country=profile.shipping_address.country,
                        zip_code=profile.shipping_address.zip_code,
                        address_type='B'
                    )
                    order.billing_address = profile.billing_address
                    order.save()
                # Billing Address Logic
                elif use_default_billing:
                    if profile.billing_address:
                        order.billing_address = profile.billing_address
                        order.save()
                    else:
                        messages.info(
                            request, 'No default billing address available')
                        return redirect('shop:checkout')
                elif same_billing_address:
                    order_billing_address = Address(
                        user=profile,
                        address_line_1=order_shipping_address.address_line_1,
                        address_line_2=order_shipping_address.address_line_2,
                        country=order_shipping_address.country,
                        zip_code=order_shipping_address.zip_code,
                        address_type='B'
                    )
                    order_billing_address.address_type = 'B'
                    order_billing_address.save()
                    order.billing_address = order_billing_address
                # User is entering in new address
                else:
                    billing_address_1 = form.cleaned_data.get(
                        'billing_address_1')
                    billing_address_2 = form.cleaned_data.get(
                        'billing_address_2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip_code = form.cleaned_data.get(
                        'billing_zip_code')
                    # Check form is not empty, cant use form because fields are not required in model
                    if is_valid_form([billing_address_1, billing_country, billing_zip_code]):
                        order_billing_address = Address(
                            user=profile,
                            address_line_1=billing_address_1,
                            address_line_2=billing_address_2,
                            country=billing_country,
                            zip_code=billing_zip_code,
                            address_type='B'
                        )
                        order_billing_address.save()
                        order.billing_address = order_billing_address
                        order.save()
                        # set default billing if user checked set default in form
                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            if set_default_billing:
                                profile.billing_address = order_billing_address
                    else:
                        messages.info(
                            request, 'Please fill in the required billing address fields')
                        return redirect('shop:checkout')

                profile.current_order = order
                profile.save()

                # Check payment option and redirect as needed
                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'stripe' or 'cash' or 'paypal':
                    return redirect('shop:payment', payment_option=payment_option)
                else:
                    messages.info(
                        request, 'Bad Payment option')
                    return redirect('shop:home')

            # Bad form input
            else:
                messages.warning(
                    request, 'There was an error while processing your input')
                return redirect('shop:checkout')
        except ObjectDoesNotExist:
            messages.info(request, 'You do not have an active order')
            return redirect('shop:home')


class PaymentView(View):
    def get(self, request, *args, **kwargs):
        # Check order exists
        try:
            profile = ShopProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            messages.info(request, 'You do not have a shop profile')
            return redirect('shop:home')
        try:
            order = Order.objects.get(
                user=profile, ordered=False)
            order_items = OrderItem.objects.filter(order=order, ordered=False)
            if order.billing_address:
                # Check payment option
                payment_option = self.kwargs['payment_option']
                if payment_option == 'stripe' or 'cash' or 'paypal':
                    context = {
                        'order': order,
                        'order_items': order_items,
                        'show_cart_coupon': False,
                        'payment_option': payment_option
                    }

                    if profile.one_click_purchasing:
                        cards = stripe.Customer.list_sources(
                            profile.stripe_cutomer_id,
                            limit=3,
                            object='card'
                        )
                        card_list = cards['data']
                        if len(card_list) > 0:
                            context.update({'card': card_list[0]})
                    return render(request, 'shop/payment.html', context)
                # bad form input
                else:
                    messages.warning(
                        request, 'Bad payment option choice')
                    return redirect('shop:home')
            else:
                messages.warning(
                    request, 'You have not added a billing address')
                return redirect('shop:checkout')
        except ObjectDoesNotExist:
            messages.info(request, 'You do not have an active order')
            return redirect('shop:home')

    def post(self, request, *args, **kwargs):
        # Check order exists
        try:
            profile = ShopProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            messages.info(request, 'You do not have a shop profile')
            return redirect('shop:home')
        try:
            order = Order.objects.get(
                user=profile, ordered=False)
            # Check form is valid
            form = PaymentForm(request.POST)

            if form.is_valid():
                save = form.cleaned_data.get('save')
                token = form.cleaned_data.get('stripeToken')
                use_default = form.cleaned_data.get('use_default')

                if save:
                    if not profile.stripe_customer_id:
                        customer = stripe.Customer.crate(
                            email=request.user.profile.email,
                            source=token
                        )
                        profile.stripe_cutomer_id = customer['id']
                        profile.one_click_purchasing = True
                        profile.save()
                    else:
                        stripe.Customer.create_source(
                            profile.stripe_customer_id,
                            source=token
                        )

                amount = int(order.get_total())
                payment = Payment()
                payment.user = profile
                payment.amount = amount

                # Cash payment
                if self.kwargs['payment_option'] == 'cash':
                    payment_option = 'cash'

                # Stripe payment
                elif self.kwargs['payment_option'] == 'stripe':
                    payment_option = 'stripe'
                    if use_default:
                        charge = stripe.Charge.create(
                            amount=amount,
                            currency='usd',
                            source=profile.stripe_customer_id
                        )
                    else:
                        charge = stripe.Chrage.create(
                            amount=amount,
                            currency='usd',
                            source=token
                        )

                # Paypal payment
                elif self.kwargs['payment_option'] == 'paypal':
                    messages.info(request, 'PAYPAL')
                    return redirect('shop:home')

                else:
                    messages.info(request, 'Incorrect payment method')
                    return redirect('shop:home')

                # Save payment add to order
                payment.payment_option = payment_option
                payment.ref_code = order.ref_code
                payment.save()
                order.payment = payment
                order.ordered_date = datetime.now()
                order.ordered = True
                order.save()
                profile.current_order = None
                profile.save()

                # update order items to ordered = true
                order_items = OrderItem.objects.filter(
                    order=order, ordered=False)
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                # TODO: Add coupon to user profile redeemed coupons
                # profile.redeemend_coupons.add(coupon)
                # TODO: Send email to admin  and user on payment submit

                messages.info(request, 'Order successful')
                return redirect('shop:home')
            else:
                messages.info(request, 'Invalid form input')
                return redirect('shop:home')

        except ObjectDoesNotExist:
            messages.info(request, 'You do not have an active order')
            return redirect('shop:home')


class OrderSummaryView(View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(
                user=request.user.shopprofile, ordered=False)
            order_items = OrderItem.objects.filter(order=order, ordered=False)
            context = {
                'order': order,
                'order_items': order_items
            }
            return render(request, 'shop/order_summary.html', context)
        except ObjectDoesNotExist:
            return render(request, 'shop/order_summary.html')


class RequestRefundVew(View):
    def get(self, request, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(request, 'shop/request_refund.html', context)

    def post(self, request, *args, **kwargs):
        form = RefundForm(request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                refund = Refund(order=order)
                refund.reason = message
                refund.email = email
                refund.ref_code = order.ref_code
                refund.username = request.user.profile.username
                refund.save()
                messages.info(request, ' Your request has been received')
                return redirect('shop:request_refund')

                # TODO: Send  email to admin on refund request in RequestRefundView POST method

            except ObjectDoesNotExist:
                messages.info(request, 'You do not have an active order')
                return redirect('shop:request_refund')

        else:
            messages.info(request, 'Invalid form input')
            return redirect('shop:request_refund')


class UploadShopItems(View):
    def get(self, request, *args, **kwargs):

        form = ShopItemsUploadForm()
        context = {'form': form}
        return render(request, "shop/csv_form.html", context)

    def post(self, request, *args, **kwargs):
        form = ShopItemsUploadForm(request.POST, request.FILES or None)
        if form.is_valid():
            file = request.FILES['csv_file']
            # Check iif CSV file
            if not file.name.endswith('.csv'):
                messages.info(request, 'This s not a CSV file')
                return redirect('admin:shop_item_changelist')
            # Upload csv file function in shop/utisl.py
            if upload_shop_data(file):
                messages.info(request, 'File successfully uploaded')
                return redirect('admin:shop_item_changelist')
            else:
                # TODO: Improve upload_shop_data error checking in shop/views.py
                messages.warning(request, 'File upload unsucessful')
                return redirect('admin:shop_item_changelist')
        else:
            messages.info(request, 'Invalid file format')
            return redirect('admin:shop_item_changelist')
