import json
from urllib import request
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from carts.models import CartItem
import orders
import requests

from store.models import Product
from .forms import OrderForm
import datetime
from .models import Order, Payment
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Payment, OrderProduct


# def payments(request):
#     return render(request, 'orders/payments.html')


def place_order(request, total=0, quantity=0,):
    # return render(request, 'orders/payments.html')
    # return HttpResponse('ok')
    current_user = request.user

    # if the cart count is less than 0, then redirect back to shop

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    print(f'cartcount: {cart_count}')
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    delivery = 50
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    grand_total = total + delivery
    print(request.method)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information in the order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line = form.cleaned_data['address_line']
            data.district = form.cleaned_data['district']
            data.province = form.cleaned_data['province']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.delivery = delivery
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            context = {
                'order': data,
                'cart_items': cart_items,
                'total': total,
                'delivery': delivery,
                'grand_total': grand_total,
            }
            print('payments')
            return render(request, 'orders/payments.html', context)
        else:
            print(form.errors)
            return redirect('checkout')
            # return HttpResponseRedirect(request, 'orders/payments.html', context)
    else:
        print('in else')
        return redirect('checkout')


@csrf_exempt
def verify_payment(request):
    data = request.body
    data = json.loads(data)
    print(data)
    order_number = int(data['product_identity'].replace('order_', ''))
    token = data['token']
    amount = data['amount']

    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {
        "token": token,
        "amount": amount,
    }
    headers = {
        "Authorization": "Key test_secret_key_1fe361df695f4be189d6b9cd9f7ece88"
    }

    response = requests.post(url, payload, headers=headers)

    if response.ok:
        data = response.json()
        print(data)
        print(order_number)
        order = Order.objects.get(
            order_number=order_number)

        # store the transaction details inside payment model
        payment = Payment(
            user=request.user,
            payment_id=data['idx'],
            payment_method=data['type']['name'],
            amount_paid=data['amount']/100,
            status='PAID',
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.status = 'Accepted'
        order.save()

        # Move the cart item to order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            # cart_item = CartItem.objects.get(id=item.id)
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.save()

        # Reduce the quantity of the sold product
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # clear cart
            CartItem.objects.filter(user=request.user).delete()

        # Send order number and payment id back to sendData method via JsonResponse
        data = {
            'order_number': order.order_number,
            'payment_id': payment.payment_id,
        }
        return JsonResponse(data=data)
    data = response.json()
    return JsonResponse(data=data, status=400)


def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=payment_id)
        context = {

            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'payment_id': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)

    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
