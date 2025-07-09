from django.contrib import admin
from .models import *
from django import forms
from django.utils.safestring import mark_safe

from django.utils.html import format_html
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

 # custom JS we'll create next

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


# @admin.register(MediaComment)
# class MediaCommentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'media', 'comment', 'timestamp')
#     search_fields = ('user__username', 'media__title', 'comment')
#     list_filter = ('timestamp',)


class BookOrderItemInline(admin.TabularInline):
    model = BookOrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'get_total']
    can_delete = False

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = "Total"

@admin.register(BookOrder)
class BookOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'email', 'tx_ref', 'status', 'total', 'created']
    list_filter = ['status',]
    search_fields = ['full_name', 'phone', 'email', 'tx_ref']
    readonly_fields = ['created', 'total', 'tx_ref']
    inlines = [BookOrderItemInline]

    fieldsets = (
        (None, {
            'fields': ('full_name', 'phone', 'email', 'status')
        }),
        ('Transaction Details', {
            'fields': ('tx_ref', 'shipping_fee', 'discount', 'total', 'created')
        }),
    )

# @admin.register(BookOrderItem)
# class BookOrderItemAdmin(admin.ModelAdmin):
#     list_display = ['id', 'order', 'product', 'quantity', 'price', 'get_total']
#     readonly_fields = ['get_total']

#     def get_total(self, obj):
#         return obj.get_total()
#     get_total.short_description = "Total"




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




