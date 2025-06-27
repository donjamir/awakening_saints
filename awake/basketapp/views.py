from django.shortcuts import render, get_object_or_404
from .basket import cartbasket
from django.http import JsonResponse
from ecomapp.models import Product
import json
from django.core.serializers.json import DjangoJSONEncoder

# Show cart page
def basket_summary(request):
    cart = cartbasket(request)
    return render(request, 'cart/basketapp/cart.html', {'cart': cart})

# Add product to cart
def cart_add(request):
    basket = cartbasket(request)
    if request.POST.get('action') == 'post':
        try:
            product_id = int(request.POST.get('product_id'))
            product_qty = int(request.POST.get('productqty'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid product ID or quantity'}, status=400)

        product = get_object_or_404(Product, id=product_id)
        basket.add(product=product, qty=product_qty)

        return JsonResponse({
            'message': 'Product added',
            'product_id': product_id,
            'qty': product_qty
        })
    return JsonResponse({'error': 'Invalid action'}, status=400)

# Update product quantity in cart
def cart_update(request):
    basket = cartbasket(request)
    if request.POST.get('action') == 'post':
        try:
            product_id = int(request.POST.get('productid'))
            product_qty = int(request.POST.get('productqty'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        basket.update(product=product_id, qty=product_qty)

        return JsonResponse({
            'qty': basket.__len__(),
            'subtotal': basket.get_total_price()
        })
    return JsonResponse({'error': 'Invalid action'}, status=400)

# Remove product from cart
def cart_delete(request):
    cart = cartbasket(request)
    if request.POST.get('action') == 'post':
        try:
            product_id = int(request.POST.get('productid'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid product ID'}, status=400)

        cart.delete(product=product_id)

        return JsonResponse({
            'subtotal': cart.get_total_price(),
            'qty': cart.__len__()
        })
    return JsonResponse({'error': 'Invalid action'}, status=400)


# def checkout(request):
#     return render(request, 'cart/basketapp/checkout.html')

def checkout_view(request):
    basket = cartbasket(request)  # ⬅ Creates the basket object

    cart_items = []

    for item in basket:  # ⬅ This uses __iter__(), which injects 'product'
        product = item.get('product')
        if product is None:
            continue

        cart_items.append({
            'id': product.id,
            'name': product.title,
            'price': float(item['price']),
            'qty': item['qty']
        })

    cart_json = json.dumps(cart_items, cls=DjangoJSONEncoder)

    return render(request, 'cart/basketapp/checkout.html', {
        'cart_json': cart_json
    })



def confirmation(request):
    return render(request, 'cart/basketapp/confirmation.html')

def tracking(request):
    return render(request, 'cart/basketapp/tracking.html')