import json
from urllib import request
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order
import requests
from django.views.decorators.csrf import csrf_exempt


def payments(request):
    return render(request, 'orders/payments.html')

# Create your views here.
def place_order(request, total=0, quantity=0,):
    # return HttpResponse('OK')
    current_user=request.user

    # if the cart count is less than 0, then redirect back to shop

    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('store')
    
    grand_total=0
    delivery=50
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    grand_total = total + delivery

    if request.method=='POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information in the order table 
            data=Order()
            data.user=current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total=grand_total
            data.delivery= delivery
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order=Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context={
                'order':order,
                'cart_items': cart_items,
                'total':total,
                'delivery':delivery,
                'grand_total':grand_total,
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')

@csrf_exempt
def verify_payment(request):
   data = request.POST
   product_id = data['product_identity']
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
   

   response = requests.post(url, payload, headers = headers)
   
   response_data = json.loads(response.text)
   status_code = str(response.status_code)

   if status_code == '400':
      response = JsonResponse({'status':'false','message':response_data['detail']}, status=500)
      return response

   import pprint 
   pp = pprint.PrettyPrinter(indent=4)
   pp.pprint(response_data)
   
   return JsonResponse(f"Payment Successful !!{response_data['user']['idx']}",safe=False)


