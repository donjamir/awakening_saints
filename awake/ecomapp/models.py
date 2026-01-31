from django.db import models
from django.conf import settings
from django.urls import reverse
from .utils import extract_text_from_file
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone


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
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_creator')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, default='admin')
    description = CKEditor5Field(blank=True, null=True)
    product_image = models.ImageField(upload_to='product_images/', default='product_images/p2.jpg')
    product_slug = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=30, decimal_places=2)
    qty_in_stock = models.DecimalField(max_digits=20, decimal_places=0, default='0')
    book_file = models.FileField(upload_to='books/', blank=True, null=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    products = ProductManager()

    class Meta:
        verbose_name_plural = 'products'
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        self.in_stock = self.qty_in_stock > 0
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('sales:product_detail', args=[self.product_slug])

    def __str__(self):
        return self.title


# In your models.py, update the BookOrder model to include payment_method field:

class BookOrder(models.Model):
    """Order model for PesaPal payments ONLY"""
    
    # Order Statuses
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'collected'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Payment'),
        (STATUS_PAID, 'Paid & Ready'),
        (STATUS_FAILED, 'Payment Failed'),
    ]
    
    # PesaPal Payment Statuses
    PAYMENT_PENDING = 'pending'
    PAYMENT_COMPLETED = 'completed'
    PAYMENT_FAILED = 'failed'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_COMPLETED, 'Completed'),
        (PAYMENT_FAILED, 'Failed'),
    ]
    
    # Payment Method Choices (PesaPal only)
    PAYMENT_METHOD_CHOICES = [
        ('pesapal', 'PesaPal'),
    ]
    
    # Customer Information
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='book_orders')
    
    # Address for PesaPal
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True, default='Kampala')
    country = models.CharField(max_length=100, blank=True, null=True, default='Uganda')
    
    # Order Reference (for PesaPal)
    tx_ref = models.CharField(max_length=100, unique=True)  # PesaPal transaction reference
    
    # Financial Information
    subtotal = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    
    # Currency (USD for Uganda via PesaPal)
    currency = models.CharField(max_length=3, default='USD')
    
    # PesaPal Specific Fields
    pesapal_tracking_id = models.CharField(max_length=255, blank=True, null=True)
    pesapal_order_id = models.CharField(max_length=255, blank=True, null=True)
    pesapal_redirect_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='pesapal')  # ADDED THIS FIELD
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    # Order Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    # Timestamps
    
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    

    class Meta:
        ordering = ('-created',)
        indexes = [
            models.Index(fields=['tx_ref']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]

    def save(self, *args, **kwargs):
        # Auto-update payment date when payment is completed
        if self.payment_status == self.PAYMENT_COMPLETED and not self.payment_date:
            self.payment_date = timezone.now()
            self.paid_at = timezone.now()
            self.status = self.STATUS_PAID
        
        # Auto-update status when payment fails
        elif self.payment_status == self.PAYMENT_FAILED:
            self.status = self.STATUS_FAILED
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PesaPal Order #{self.id} - {self.full_name} - ${self.total}"

    @property
    def is_paid(self):
        """Check if order is paid via PesaPal"""
        return self.payment_status == self.PAYMENT_COMPLETED

    @property
    def can_download(self):
        """Check if order can be downloaded (paid via PesaPal)"""
        return self.status == self.STATUS_PAID and self.payment_status == self.PAYMENT_COMPLETED


class BookOrderItem(models.Model):
    order = models.ForeignKey(BookOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    downloaded = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def get_total(self):
        if self.price is None or self.quantity is None:
            return 0
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class PaymentLog(models.Model):
    """Log all PesaPal payment activities"""
    order = models.ForeignKey(BookOrder, on_delete=models.CASCADE, related_name='payment_logs')
    
    # PesaPal Tracking
    pesapal_tracking_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Payment Status
    status_code = models.CharField(max_length=10)
    status_description = models.TextField()
    
    # Raw Data from PesaPal
    ipn_data = models.JSONField(default=dict)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"PesaPal Log - {self.order.tx_ref} - {self.status_code}"


# Other existing models (unchanged)
class BookPreview(models.Model):
    book = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='preview')
    chapter_title = models.CharField(max_length=255)
    content = CKEditor5Field() 

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


class SermonContent(models.Model):
    MEDIA_TYPES = [
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('text', 'Text'),
    ]

    title = models.CharField(max_length=255)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='media_files/', blank=True, null=True)
    text_body = CKEditor5Field(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='media_thumbnails/', blank=True, null=True)
    preacher = models.CharField(max_length=255, blank=True)
    scripture = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.media_type == 'text' and self.file and not self.text_body:
            try:
                self.text_body = extract_text_from_file(self.file.path)
            except Exception as e:
                print(f"Text extraction failed: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.media_type.upper()}: {self.title}"

    def get_file_url(self):
        return self.file.url if self.file else ""

    def get_thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else ""

    def get_excerpt(self, words=30):
        if self.media_type == 'text' and self.text_body:
            return ' '.join(self.text_body.split()[:words]) + '...'
        return ""


class SermonComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media = models.ForeignKey(SermonContent, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.first_name } on {self.media.title}"

    def as_dict(self):
        return {
            "username": self.user.get_full_name() or self.user.first_name,
            "text": self.comment,
            "timestamp": self.timestamp.strftime("%b %d, %Y"),
        }


class EmailSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class SubscriberMessage(models.Model):
    title = models.CharField(max_length=255)
    body = CKEditor5Field() 
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title