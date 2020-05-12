from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core.views import CustomSignupView

urlpatterns = [
    # path('', include('core.urls', namespace='core')),
    path('', include('shop.urls', namespace='shop')),
    path('accounts/', include('allauth.urls')),
    path('accounts/signup', CustomSignupView.as_view(), name='account_signup'),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

# Admin customization

admin.site.site_header = "ScubaDiveDubai Admin"
admin.site.site_title = "ScubaDiveDubai Admin"
admin.site.index_title = "Welcome to ScubaDiveDubai Admin"


# ALLAUTH URLS

# accounts/signup/ [name='account_signup']
# accounts/login/ [name='account_login']
# accounts/logout/ [name='account_logout']
# accounts/password/change/ [name='account_change_password']
# accounts/password/set/ [name='account_set_password']
# accounts/inactive/ [name='account_inactive']
# accounts/email/ [name='account_email']
# accounts/confirm-email/ [name='account_email_verification_sent']
# accounts/confirm-email/(?P<key>[-:\w]+)/ [name='account_confirm_email']
# accounts/password/reset/ [name='account_reset_password']
# accounts/password/reset/done/ [name='account_reset_password_done']
# accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/ [name='account_reset_password_from_key']
# accounts/password/reset/key/done/ [name='account_reset_password_from_key_done']
# accounts/social/
