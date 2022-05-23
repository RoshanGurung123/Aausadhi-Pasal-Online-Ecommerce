from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.


class OrderAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'payment',
        'first_name',
        'last_name',
        'order_number',
        'is_ordered',
    ]


class PaymentAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'payment_id',
        'payment_method',
        'amount_paid',
    ]


class OrderProductAdmin(admin.ModelAdmin):

    list_display = [
        'product',
        'user',
        'payment',
    ]


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
