from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views
from . import utils

app_name = 'shop'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug>/', views.CategoryDetailView.as_view(),
         name='category_detail'),
    path('product/<slug>/', views.ProductView.as_view(), name='product'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order_summary'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    path('request-refund/', views.RequestRefundVew.as_view(), name='request_refund'),
    path('upload-shop-items/', views.UploadShopItems.as_view(),
         name='upload_shop_items'),
    path('add-coupon/', utils.add_coupon, name='add_coupon'),
    # Utils
    path('add-to-cart/<slug>/', utils.add_to_cart, name='add_to_cart'),
    path('remove-single-cart/<slug>/', utils.remove_single_item_from_cart,
         name='remove_single_item_from_cart'),
    path('remove-from-cart/<slug>/',
         utils.remove_from_cart, name='remove_from_cart'),
    path('delete-cart/',
         utils.delete_cart, name='delete_cart')
]
