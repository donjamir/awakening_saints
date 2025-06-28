from .basket import cartbasket

def cart(request):
    return { 'cart': cartbasket(request)}