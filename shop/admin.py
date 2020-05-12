import csv
import string

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.forms.models import model_to_dict

from .models import (Address, Brand, Category, Color, Coupon, Item,
                     ItemInfo, Label, Order, OrderItem, Payment, Refund,
                     ShopProfile, Size)

# TODO: Change list_display_links to direct to current_order in ShopProfileAdmin in shop/admin.py


class ShopProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'first_name',
        'last_name',
        'current_order',
        'billing_address'
    ]

    list_display_links = ['user',
                          'billing_address',
                          'current_order',
                          ]


class ExportCsvMixin:

    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        label = meta.label_lower.split('.')
        filename = f'{label[0]}_{label[1]}.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'

        writer = csv.writer(response)
        # Check model type to ensure proper export
        if filename == 'shop_item.csv':
            item_info_fields = ['title', 'text']
            writer.writerow(field_names)
            for obj in queryset:
                item = [getattr(obj, field)
                        for field in field_names]
                for item_info in obj.item_info.all():
                    item.append(item_info)
                row = writer.writerow(item)

            return response

        else:
            writer.writerow(field_names)
            for obj in queryset:
                row = writer.writerow([getattr(obj, field)
                                       for field in field_names])
            return response

    export_as_csv.short_description = 'Export Selected'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'on_delivery',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'start_date',
                    'ordered_date',
                    'billing_address',
                    'shipping_address',
                    'payment',
                    'coupon'
                    ]

    list_filter = ['user',
                   'ordered',
                   'on_delivery',
                   'received',
                   'refund_requested',
                   'refund_granted',
                   'start_date',
                   'ordered_date'
                   ]

    list_display_links = ['user',
                          'billing_address',
                          'shipping_address',
                          'payment',
                          'coupon'
                          ]

    search_fields = ['user__username', 'ref_code']

    def accept_refund(self, request, queryset):
        queryset.update(refund_requested=False, refund_granted=True)

    actions = [accept_refund]

    accept_refund.short_description = 'Update orders to refund granted'

    # Filter items to only show items within selected order

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     order_number = request.path_info.split('/')[4]
    #     order = Order.objects.filter(pk=order_number)[0]
    #     if db_field.name == "items":
    #         kwargs["queryset"] = OrderItem.objects.filter(
    #             ref_code=order.ref_code)
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'address_line_1',
        'address_line_2',
        'country',
        'zip_code',
        'address_type',
    ]

    list_filter = [
        'address_type',
        'country'
    ]

    search_fields = [
        'user'
        'address_line_1'
        'address_line_2'
        'zip_code'
    ]


class ItemAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = 'shop/items_changelist.html'

    list_display = [
        'title',
        'sku',
        'category',
        'price',
        'discount_price',
        'stock_count',
        'brand',
        'size',
    ]

    list_filter = [
        'brand',
        'category',
        'stock_count',
    ]

    search_fields = [
        'title',
        'brand',
        'category',
    ]

    actions = ['export_as_csv']


class ShopAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = 'shop/items_changelist.html'
    actions = ['export_as_csv']


admin.site.register(Order, OrderAdmin)
admin.site.register(ShopProfile, ShopProfileAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Category, ShopAdmin)
admin.site.register(Brand, ShopAdmin)
admin.site.register(Color, ShopAdmin)
admin.site.register(Label, ShopAdmin)
admin.site.register(Size, ShopAdmin)
admin.site.register(ItemInfo, ShopAdmin)
