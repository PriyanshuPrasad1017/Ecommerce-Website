import json
from .models import *

def cookieCart(request):
    try: # creating empty cart for non logged in user
        cart = json.loads(request.COOKIES['cart']) # name of our cookie is 'cart', json.loads will convert it from string to python dictionary
    except:
        cart = {}
    # cart[productId] = {'quantity' : 1} <- this is how cookie cart looks like
    items = []
    order = {'get_cart_total' : 0, 'get_cart_items' : 0, 'shipping' : False}
    cartItems = order['get_cart_items']
    for i in cart: # i is productId
        try: 
            if(cart[i]['quantity'] > 0):
                cartItems += cart[i]['quantity']
                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])
                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'id' : product.id,
                    'product' : {
                        'id' : product.id,
                        'name' : product.name,
                        'price' : product.price,
                        'imageURL' : product.imageURL,
                        },
                    'quantity' : cart[i]['quantity'],
                    'get_total' : total,
                    'digital' : product.digital
                }
                items.append(item)
                if product.digital == False:
                    order['shipping'] = True
        except:
            pass
    return {'cartItems' : cartItems, 'order' : order, 'items' : items}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all() #  get all items in order
        cartItems = order.get_cart_items # no of items in the cart
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems' : cartItems, 'order' : order, 'items' : items}

def guestOrder(request, data):
    print('User is not logged in')
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']
    cookieData = cookieCart(request)
    items = cookieData['items']
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()
    order = Order.objects.create(
        customer=customer,
        complete=False,
        )
    for item in items:
        product = Product.objects.get(id=item['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    
    return customer, order