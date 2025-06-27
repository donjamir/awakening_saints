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
    path('orphans/', views.orphans, name='orphans'),
    path('books/', views.books, name='books'),


    path('add-review/', views.add_review_ajax, name='add_review_ajax'),
    path('book-preview/<slug:product_slug>/', views.book_preview, name='book_preview'),

    path('shop-home', views.index, name='books' ),
    path('shop/<slug:cat_slug>', views.shop, name='shop_list'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('blog-details/', views.single_blog, name='blog1'),
    path('product-details/<slug:product_slug>/', views.single_product, name='product_detail'),
   
]