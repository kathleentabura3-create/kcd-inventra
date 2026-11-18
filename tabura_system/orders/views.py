from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product
from .models import Order, OrderItem
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render

@login_required
def profile_view(request):
    # You can also fetch user-specific orders here later if you want!
    return render(request, 'users/profile.html')


def update_cart_quantity(request, product_id):
    action = request.GET.get('action')
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if action == 'increase':
            if cart[product_id_str]['quantity'] + 1 > product.stock:
                messages.error(request, f"Cannot add more. Only {product.stock} units available.")
            else:
                cart[product_id_str]['quantity'] += 1
        elif action == 'decrease':
            cart[product_id_str]['quantity'] -= 1
            if cart[product_id_str]['quantity'] <= 0:
                del cart[product_id_str]
                
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('cart_detail')


@login_required
def dashboard_view(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    recent_orders = user_orders[:5]
    context = {
        'orders': user_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'orders/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('product_list')



def checkout_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        shipping_address = request.POST.get('shipping_address')
        quantity = int(request.POST.get('quantity', 1))

        # Check if enough stock is available
        if quantity > product.stock:
            error_message = f"Sorry, only {product.stock} items left in stock."
            return render(request, 'orders/checkout.html', {'product': product, 'error': error_message})

        # Calculate total price
        total_amount = product.price * quantity

        # Create the Order
        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            shipping_address=shipping_address,
            total_amount=total_amount,
            status='Pending'
        )

        # Create the OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        # Deduct stock from inventory
        product.stock -= quantity
        product.save()

        # Redirect to the success page with the order ID
        return redirect('order_success', order_id=order.id)

    return render(request, 'orders/checkout.html', {'product': product})

def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})


def order_history_view(request):
    # Fetch all orders, newest first
    orders = Order.objects.all().order_by('-id')
    return render(request, 'orders/order_history.html', {'orders': orders})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    # If product already in cart, increase quantity, otherwise set to 1
    str_id = str(product_id)
    if str_id in cart:
        cart[str_id]['quantity'] += 1
    else:
        cart[str_id] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'stock': product.stock
        }

    request.session['cart'] = cart
    
    # Stay on the current page (Storefront) instead of jumping to the cart
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('product_list')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, item_data in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = float(item_data['price']) * item_data['quantity']
        total += subtotal
        cart_items.append({
            'id': product_id,
            'product': product,
            'name': item_data['name'],
            'price': item_data['price'],
            'quantity': item_data['quantity'],
            'subtotal': subtotal,
        })

    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total': total})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    str_id = str(product_id)
    if str_id in cart:
        del cart[str_id]
        request.session['cart'] = cart
    return redirect('cart_detail')

def cart_checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart_detail')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        shipping_address = request.POST.get('shipping_address')

        # Calculate total amount
        total_amount = sum(item['price'] * item['quantity'] for item in cart.values())

        # Create the main Order
        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            shipping_address=shipping_address,
            total_amount=total_amount,
            status='Pending'
        )

        # Loop through each item in the session cart
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            quantity = item['quantity']

            # Check stock safety
            if quantity > product.stock:
                # If stock changed, show error on cart page
                total = sum(i['price'] * i['quantity'] for i in cart.values())
                return render(request, 'orders/cart.html', {
                    'cart': cart, 
                    'total': total, 
                    'error': f"Sorry, {product.name} only has {product.stock} items left in stock."
                })

            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item['price']
            )

            # Deduct stock
            product.stock -= quantity
            product.save()

        # Clear the session cart after successful order
        request.session['cart'] = {}

        return redirect('order_success', order_id=order.id)

    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'orders/cart_checkout.html', {'cart': cart, 'total': total})



def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'orders/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'orders/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('product_list')

