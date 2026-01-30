from django.contrib import admin
from .models import *
from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html_join

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cat_name','cat_slug')
    prepopulated_fields = {'cat_slug': ('cat_name',)}
    search_fields = ('cat_name',)



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_image_display', 'product_price', 'qty_in_stock', 'stock_status', 'is_active')
    list_filter = ['in_stock', 'is_active']
    prepopulated_fields = {'product_slug': ('title',)}
    list_editable = ['product_price', 'qty_in_stock']
    search_fields = ('title',)

    def stock_status(self, obj):
        if obj.in_stock:
            return format_html('<span style="color:green;">In Stock</span>')
        return format_html('<span style="color:red; font-weight:bold;">OUT OF STOCK</span>')
    stock_status.short_description = "Stock Status"

    def product_image_display(self, obj):
        if obj.product_image:
            return format_html('<img src="{}" style="height: 50px;" />', obj.product_image.url)
        return "-"
    product_image_display.short_description = "Image"



# -----------------------------
# BookPreview Admin
# -----------------------------

@admin.register(BookPreview)
class BookPreviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'chapter_title')
    search_fields = ('book__title', 'chapter_title')
    autocomplete_fields = ('book',)

# -----------------------------
# BookReview Admin
# -----------------------------

# @admin.register(BookReview)
# class BookReviewAdmin(admin.ModelAdmin):
#     list_display = ('user', 'book','comment', 'rating', 'timestamp')
#     list_filter = ('rating', 'timestamp')
#     search_fields = ('user__name', 'book__title', 'comment')
#     autocomplete_fields = ('user', 'book')

# -----------------------------
# MediaContent Admin
# -----------------------------

class MediaCommentInline(admin.TabularInline):
    model = SermonComment
    extra = 0
    readonly_fields = ('user', 'comment', 'timestamp')
    can_delete = True


class MediaContentAdminForm(forms.ModelForm):
    class Meta:
        model = SermonContent
        fields = '__all__'

    class Media:
        js = ('admin/js/media_toggle.js',)  # See JS file below


@admin.register(SermonContent)
class MediaContentAdmin(admin.ModelAdmin):
    form = MediaContentAdminForm
    inlines = [MediaCommentInline]

    list_display = ('id', 'title', 'media_type', 'uploaded_at')
    list_filter = ('media_type', )
    search_fields = ('title',)
    readonly_fields = ('uploaded_at', 'file_preview',)

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'media_type',
                'file',
                'thumbnail',
                'text_body',
                'file_preview'
            )
        }),
        ('Metadata', {
            'fields': ('scripture', 'preacher', 'description', 'uploaded_at')
        }),
    )

    def file_preview(self, obj):
        if obj.media_type == 'audio' and obj.file:
            return mark_safe(f"<audio controls style='max-width: 300px;'><source src='{obj.file.url}' type='audio/mpeg'></audio>")
        elif obj.media_type == 'video' and obj.file:
            return mark_safe(f"<video controls style='max-width: 300px; height: auto;'><source src='{obj.file.url}' type='video/mp4'></video>")
        elif obj.media_type == 'text' and obj.text_body:
            return mark_safe(f"<div style='max-width: 400px; white-space: pre-wrap;'>{obj.get_excerpt(50)}</div>")
        return "No preview available."

    file_preview.short_description = 'Preview'


class BookOrderItemInline(admin.TabularInline):
    model = BookOrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'get_total', 'download_status']
    can_delete = False

    def get_total(self, obj):
        return f"${obj.get_total():.2f}"
    get_total.short_description = "Item Total"

    def download_status(self, obj):
        if obj.downloaded:
            return format_html('<span style="color:green; font-weight:bold;">✓ Downloaded</span>')
        return format_html('<span style="color:orange;">Pending</span>')
    download_status.short_description = "Download Status"


@admin.register(BookOrder)
class BookOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'email', 'tx_ref', 'payment_status_badge', 'total_display', 'created', 'pesapal_actions']
    list_filter = ['status', 'payment_status', 'created']
    search_fields = ['full_name', 'phone', 'email', 'tx_ref', 'pesapal_tracking_id']
    readonly_fields = ['created', 'updated', 'paid_at', 'subtotal', 'total', 'tx_ref', 'payment_date', 'pesapal_links']
    inlines = [BookOrderItemInline]
    actions = ['mark_as_paid', 'mark_as_failed', 'resend_pesapal_link']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('full_name', 'phone', 'email', 'user')
        }),
        ('Shipping Information', {
            'fields': ('address', 'city', 'country')
        }),
        ('Order Details', {
            'fields': ('tx_ref', 'subtotal', 'total', 'currency')
        }),
        ('PesaPal Payment Details', {
            'fields': ('payment_status', 'status', 'pesapal_tracking_id', 'pesapal_order_id', 'payment_date', 'pesapal_links')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated', 'paid_at')
        }),
    )

    def payment_status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="background-color:{}; color:white; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display().upper()
        )
    payment_status_badge.short_description = "Payment Status"

    def total_display(self, obj):
        return f"${obj.total:.2f} {obj.currency}"
    total_display.short_description = "Total"

    def pesapal_links(self, obj):
        if obj.pesapal_tracking_id:
            links = []
            if obj.pesapal_redirect_url:
                links.append(f'<a href="{obj.pesapal_redirect_url}" target="_blank" class="button">PesaPal Payment Link</a>')
            
            # Status check URL for admin
            if settings.PESAPAL_ENVIRONMENT == 'sandbox':
                status_url = f'https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus?orderTrackingId={obj.pesapal_tracking_id}'
            else:
                status_url = f'https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus?orderTrackingId={obj.pesapal_tracking_id}'
            
            links.append(f'<a href="{status_url}" target="_blank" class="button">Check PesaPal Status</a>')
            
            return mark_safe('<br>'.join(links))
        return "No PesaPal tracking ID"
    pesapal_links.short_description = "PesaPal Links"

    def pesapal_actions(self, obj):
        if obj.payment_status == 'pending' and obj.pesapal_redirect_url:
            return format_html(
                '<a href="{}" target="_blank" class="button" style="background-color: #FF6B00; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">Send Payment Link</a>',
                obj.pesapal_redirect_url
            )
        elif obj.payment_status == 'completed':
            return format_html('<span style="color:green; font-weight:bold;">✓ Paid</span>')
        return "-"
    pesapal_actions.short_description = "Actions"

    @admin.action(description="Mark selected orders as paid")
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(
            payment_status='completed',
            status='collected',
            payment_date=timezone.now(),
            paid_at=timezone.now()
        )
        self.message_user(request, f"{updated} orders marked as paid.")

    @admin.action(description="Mark selected orders as failed")
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(
            payment_status='failed',
            status='failed'
        )
        self.message_user(request, f"{updated} orders marked as failed.")

    @admin.action(description="Resend PesaPal payment link")
    def resend_pesapal_link(self, request, queryset):
        for order in queryset:
            if order.pesapal_redirect_url:
                # In a real implementation, you would regenerate and send the link
                self.message_user(request, f"Payment link for order {order.tx_ref}: {order.pesapal_redirect_url}")
            else:
                self.message_user(request, f"No PesaPal link available for order {order.tx_ref}", level='warning')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_link', 'status_code', 'pesapal_tracking_id', 'created_at']
    list_filter = ['status_code', 'created_at']
    search_fields = ['order__tx_ref', 'pesapal_tracking_id', 'status_description']
    readonly_fields = ['created_at', 'order_link', 'ipn_data_display']
    date_hierarchy = 'created_at'

    def order_link(self, obj):
        url = reverse('admin:basketapp_bookorder_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.tx_ref)
    order_link.short_description = "Order"

    def ipn_data_display(self, obj):
        if obj.ipn_data:
            items = []
            for key, value in obj.ipn_data.items():
                items.append(f"<strong>{key}:</strong> {value}")
            return mark_safe('<br>'.join(items))
        return "No IPN data"
    ipn_data_display.short_description = "IPN Data"

    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'pesapal_tracking_id', 'status_code', 'status_description')
        }),
        ('IPN Data', {
            'fields': ('ipn_data_display',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(BookOrderItem)
class BookOrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_link', 'product_link', 'quantity', 'price_display', 'total_display', 'download_status']
    list_filter = ['downloaded', 'created']
    search_fields = ['order__tx_ref', 'product__title']
    readonly_fields = ['get_total', 'created']
    
    def order_link(self, obj):
        url = reverse('admin:basketapp_bookorder_change', args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = "Order"

    def product_link(self, obj):
        url = reverse('admin:basketapp_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.title)
    product_link.short_description = "Product"

    def price_display(self, obj):
        return f"${obj.price:.2f}"
    price_display.short_description = "Price"

    def total_display(self, obj):
        return f"${obj.get_total():.2f}"
    total_display.short_description = "Total"

    def download_status(self, obj):
        if obj.downloaded:
            return format_html('<span style="color:green; font-weight:bold;">✓ Downloaded</span>')
        return format_html('<span style="color:orange;">Pending</span>')
    download_status.short_description = "Download Status"


@admin.register(EmailSubscriber)
class EmailSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_on']
    search_fields = ['email']

@admin.register(SubscriberMessage)
class SubscriberMessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'sent_at', 'send_to_all']
    readonly_fields = ['sent_at']

    def send_to_all(self, obj):
        return format_html(
            '<a class="button" href="/send-message/{}/">Send</a>', obj.id
        )
    send_to_all.short_description = 'Send Action'