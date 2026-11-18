from django.shortcuts import render
from .models import Product
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Category
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm 
# Or your custom form
from django.db.models.functions import Lower



def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # <--- 'form' is defined here
        if form.is_valid():
            user = form.save()
            login(request, user) # Automatically logs them in
            return redirect('product_list') # Sends them straight to the homepage!
    else:
        form = UserCreationForm() # <--- 'form' is also defined for GET requests

    return render(request, 'users/register.html', {'form': form})

from django.db.models.functions import Lower
from .models import Product, Category

def product_list(request):
    query = request.GET.get('q')
    product_id = request.GET.get('product_id')
    category_id = request.GET.get('category')
    
    products = Product.objects.all().order_by(Lower('name'))
    categories = Category.objects.all()

    # Look at your VS Code terminal when you refresh the page!
    print("CATEGORIES IN VIEW:", categories)

    if product_id:
        products = products.filter(id=product_id)
    else:
        if category_id:
            products = products.filter(category_id=category_id)
        if query:
            products = products.filter(name__icontains=query)

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'product_id': product_id,
        'selected_category': int(category_id) if category_id else None,
    })

def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.all()
    
    if query:
        # icontains ensures it filters down to the exact item clicked from the suggestion
        products = products.filter(name__icontains=query)
        
    return render(request, 'products/product_list.html', {'products': products, 'query': query})

def product_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        # Matches products starting with the typed letters (case-insensitive)
        products = Product.objects.filter(name__istartswith=query)[:5]
        results = [{'id': p.id, 'name': p.name, 'price': str(p.price)} for p in products]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})


def product_list(request):
    query = request.GET.get('q')
    product_id = request.GET.get('product_id')
    
    # Sort all products alphabetically from A to Z (case-insensitive)
    products = Product.objects.all().order_by(Lower('name'))

    if product_id:
        # Show ONLY the specific product clicked from the dropdown
        products = products.filter(id=product_id)
    elif query:
        # Filter by search text if the user clicked the Search button
        products = products.filter(name__icontains=query)

    return render(request, 'products/product_list.html', {
        'products': products,
        'query': query,
        'product_id': product_id,
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    product_id_str = str(product_id)
    
    # Calculate current quantity in cart for this product
    current_qty_in_cart = cart.get(product_id_str, {}).get('quantity', 0)
    
    # Check if adding one more exceeds available stock
    if current_qty_in_cart + 1 > product.stock:
        messages.error(request, f"Sorry, only {product.stock} left in stock for {product.name}!")
        return redirect('product_list')
        
    # If stock is sufficient, proceed with adding/updating
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
        }
        
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Product

@login_required
def add_to_cart(request, product_id):
    # Your existing add to cart logic...
    # Because of @login_required, only logged-in users can run this function!
    product = get_object_or_404(Product, id=product_id)
    # ...
    return redirect('cart_detail')

@login_required
def checkout_view(request):
    # Your existing checkout logic...
    # Unauthenticated users will be redirected to the login page instead
    return render(request, 'orders/checkout.html')