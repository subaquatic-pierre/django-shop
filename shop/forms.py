from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('paypal', 'Paypal'),
    ('stripe', 'Stripe'),
    ('cash', 'Cash'),
)


class CheckoutForm(forms.Form):
    shipping_address_1 = forms.CharField(required=False)
    shipping_address_2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(required=False, widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100',
    }))
    shipping_zip_code = forms.CharField(required=False)

    billing_address_1 = forms.CharField(required=False)
    billing_address_2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(required=False, widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100',
    }))
    billing_zip_code = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(choices=PAYMENT_CHOICES,
                                       widget=forms.RadioSelect(attrs={
                                           'class': 'custom-control-input'
                                       }))


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': "Recipient's username",
        'aria-describedby': "basic-addon2"
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


class ShopItemsUploadForm(forms.Form):
    csv_file = forms.FileField()


# TODO: Add custom UserSignUpForm in shop/forms.py

# from django.contrib.auth import get_user_model
# from django import forms

# class SignupForm(forms.ModelForm):
    # first_name = forms.CharField(max_length=30, label='Voornaam')
    # last_name = forms.CharField(max_length=30, label='Achternaam')
#     class Meta:
#         model = get_user_model()
#         fields = ['first_name', 'last_name']

#     def signup(self, request, user):
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.save()
