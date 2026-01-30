from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [

    path('', views.indexone, name='homeone'),
    path('about/', views.about, name='about'),
    path('contact/', views.contactone, name='contact'),
    path('services/', views.services, name='services'),
    path('donate/', views.donate, name='donate'),
    path('media/', views.media, name='media'),
    path('add-comment/', views.add_comment, name='add_comment'),
    path('orphans/', views.orphans, name='orphans'),
    path('books/', views.books, name='books'),


    path('add-review/', views.add_review_ajax, name='add_review_ajax'),
    path('book-preview/<slug:product_slug>/', views.book_preview, name='book_preview'),

    path('books-home', views.index, name='books' ),
    path('shop/<slug:cat_slug>', views.index, name='shop_list'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('blog-details/', views.single_blog, name='blog1'),
    path('product-details/<slug:product_slug>/', views.single_product, name='product_detail'),
   
    path("subscribe/", views.subscribe_email, name="subscribe_email"),
    path("send-message/<int:message_id>/", views.send_message_to_subscribers, name="send_message_to_subscribers"),
    
    path('pesapal/payment/', views.pesapal_payment_request, name='pesapal_payment'),
    path('pesapal/callback/', views.pesapal_callback, name='pesapal_callback'),
    path('pesapal/ipn/', views.pesapal_ipn, name='pesapal_ipn'),
]