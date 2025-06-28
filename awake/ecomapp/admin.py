from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cat_name','cat_slug')
    prepopulated_fields = {'cat_slug': ('cat_name',)}
    search_fields = ('cat_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_image', 'product_price', 'qty_in_stock', 'in_stock', 'is_active')
    list_filter = ['in_stock', 'is_active']
    prepopulated_fields = {'product_slug': ('title',)}
    list_editable = ['product_price', 'qty_in_stock', 'in_stock']
    search_fields = ('title',)


from django.contrib import admin
from .models import BookPreview, BookReview, MediaContent, MediaComment

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

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book','comment', 'rating', 'timestamp')
    list_filter = ('rating', 'timestamp')
    search_fields = ('user__name', 'book__title', 'comment')
    autocomplete_fields = ('user', 'book')

# -----------------------------
# MediaContent Admin
# -----------------------------

@admin.register(MediaContent)
class MediaContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'file_url', 'uploaded_at')
    list_filter = ('media_type', 'uploaded_at')
    search_fields = ('title',)
    readonly_fields = ('uploaded_at',)

# -----------------------------
# MediaComment Admin
# -----------------------------

@admin.register(MediaComment)
class MediaCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'media', 'timestamp')
    search_fields = ('user__name', 'media__title', 'comment')
    list_filter = ('timestamp',)
    autocomplete_fields = ('user', 'media')



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
    list_filter = ['status', 'created']
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

@admin.register(BookOrderItem)
class BookOrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'get_total']
    readonly_fields = ['get_total']

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = "Total"


