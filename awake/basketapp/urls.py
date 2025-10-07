from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('', views.basket_summary, name='cart_summary'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirmation/', views.confirmation, name='confirm'),
    path('track/', views.tracking, name='track'),

    path('add-to-cart/', views.cart_add, name='cart_add'),
    path('delete/', views.cart_delete, name='cart_delete'),
    path('update/', views.cart_update, name='cart_update'),
    
    path('submit-order/', views.submit_order, name='submit_order'),
   
    path('download/<signed_value>/', views.download_book, name='download_book'),
 
    path('order/<int:order_id>/downloads/', views.download_page, name='download_page'),
    
    # path('payment-waiting/', views.payment_waiting, name='payment_waiting'), 
    path("payment-success/", views.payment_success, name="payment_success"),

   
]

   # path('download/<int:order_id>/<int:product_id>/', views.download_book, name='download_book'),