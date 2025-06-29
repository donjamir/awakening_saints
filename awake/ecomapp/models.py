from django.db import models
from django.conf import settings
from django.urls import reverse







class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)


class Category(models.Model):
    cat_name = models.CharField(max_length=255, db_index=True)
    cat_slug = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('sales:shop_list', args=[self.cat_slug])
    
    def __str__(self):
        return self.cat_name
    

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name='product_creator')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, default='admin')
    description = models.TextField(blank=True, null=True)
    product_image = models.ImageField(upload_to='product_images/', default='product_images/p2.jpg') 
    product_slug = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=30, decimal_places=0)
    qty_in_stock = models.DecimalField(max_digits=20, decimal_places=0, default='0')
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    products = ProductManager()

    class Meta:
        verbose_name_plural = 'products'
        ordering = ('-created',)

    # dynamic way of linking products to the url on the front end
    def get_absolute_url(self):
        return reverse('sales:product_detail', args=[self.product_slug])

    def __str__(self):
        return self.title



class BookOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready', 'Ready for Pickup'),
        ('collected', 'Collected'),
        ('cancelled', 'Cancelled'),
    ]

    full_name = models.CharField(max_length=255)  # updated from `name`
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    tx_ref = models.CharField(max_length=100, unique=True)  # transaction ref for Flutterwave
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=30, decimal_places=0, default=0)

    # note = models.TextField(blank=True, null=True)  # optional buyer message
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class BookOrderItem(models.Model):
    order = models.ForeignKey(BookOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=30, decimal_places=0)

    def get_total(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"




class BookPreview(models.Model):
    book = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='preview')
    chapter_title = models.CharField(max_length=255)
    content = models.TextField()  # Replace file with content field

    def __str__(self):
        return f"Preview of {self.book.title}"

    
class BookReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s review on {self.book.title}"

# -----------------------------
# MEDIA CONTENT (Audio/Video)
# -----------------------------

class MediaContent(models.Model):
    MEDIA_TYPES = [
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]

    title = models.CharField(max_length=255)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file_url = models.URLField()
    thumbnail = models.ImageField(upload_to='media_thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type.upper()}: {self.title}"

class MediaComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media = models.ForeignKey(MediaContent, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} on {self.media.title}"
