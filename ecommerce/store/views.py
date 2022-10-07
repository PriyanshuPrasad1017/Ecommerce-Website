
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse # returns data in html template
import json
import datetime
from .models import *
from .utils import cartData, guestOrder
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm

# Create your views here.

def signup(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if(form.is_valid()):
                user = form.save()
                username = form.cleaned_data.get('first_name')
                email = form.cleaned_data.get('email')
                Customer.objects.create(user=user, name=user.username, email=email)
                return redirect('login')
        context = {'form' : form}
        return render(request, 'registration/signup.html', context)


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products' : products, 'cartItems' : cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items' : items, 'order' : order, 'cartItems' : cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems'] # no of items in cart
    order = data['order'] # current order
    items = data['items'] # all items in the current order/cart

    context = {'items' : items, 'order' : order, 'cartItems' : cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request): 
    data = json.loads(request.body) # data from cart.js
    productId = data['productId']
    action = data['action']
    print('Action :', action)
    print('productId :', productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = orderItem.quantity + 1
    elif action == 'remove':
        orderItem.quantity = orderItem.quantity - 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body) # parsing data from fetch call in checkout.html

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
  
    else: 
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    print(total)
    print(order.get_cart_total)
    
    if total == float(order.get_cart_total):
        order.complete = True
    # order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse('Payment complete!', safe=False)

    