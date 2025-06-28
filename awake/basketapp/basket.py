from ecomapp.models import *
from decimal import Decimal

class cartbasket():
    """
    A base cartbasket class, providing some default behaviors that 
    can be inherited or overrided, as necessary
    """
    def __init__(self, request):
        
        self.session = request.session
        basket = self.session.get('cartsessionkey')
        if 'cartsessionkey' not in request.session:
            basket = self.session['cartsessionkey'] = {}
        self.basket = basket

    def add(self, product, qty):
        """ 
        Adding and Updating the users cart session data
        """
        product_id = str(product.id)
        
        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
        else:
            self.basket[product_id] = {'price': str(product.product_price), 'qty':qty}
        self.save()

    def update(self, product, qty):
        """ 
        Updating the users cart session data
        """
        product_id = str(product)
        # qty = qty

        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
        self.save()


    def delete(self, product):
        """
        Delete item from session data
        """
        product_id = str(product)
        # print(product_id)

        if product_id in self.basket:
            del self.basket[product_id]

        self.save()

    def save(self):
        self.session.modified = True


    def __iter__(self):
        product_ids = self.basket.keys()
        products = Product.products.filter(id__in=product_ids)
        basket = self.basket.copy()

        for product in products:
            pid = str(product.id)
            basket[pid]['product'] = product
            basket[pid]['name'] = product.title  # <-- add name explicitly
            basket[pid]['price'] = Decimal(basket[pid]['price'])
            basket[pid]['total_price'] = basket[pid]['price'] * basket[pid]['qty']

        for item in basket.values():
            yield item


    def __len__(self):
        """
        Get the basket data and count the qty of items 
        """
        return sum(item['qty'] for item in self.basket.values())

    def  get_total_price(self):
        return sum(Decimal(item['price']) * item['qty'] for item in self.basket.values())


