"""
Admin configuration for the shop application.
Cấu hình admin cho ứng dụng shop.
"""

from django.contrib import admin
from .models import (
    Product, 
    ProductImage, 
    StorageOption, 
    ColorOption, 
    Review, 
    Coupon,
    ShippingAddress,
    Order,
    OrderItem
)


class ProductImageInline(admin.TabularInline):
    """Hiển thị hình ảnh chi tiết inline trong trang admin sản phẩm."""
    model = ProductImage
    extra = 1


class StorageOptionInline(admin.TabularInline):
    """Hiển thị tùy chọn bộ nhớ inline."""
    model = StorageOption
    extra = 1


class ColorOptionInline(admin.TabularInline):
    """Hiển thị tùy chọn màu sắc inline."""
    model = ColorOption
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin cho model Product.
    Hiển thị danh sách sản phẩm và form thêm/sửa.
    """
    list_display = [
        'name', 
        'brand', 
        'original_price', 
        'sale_price', 
        'discount_percent',
        'created_at'
    ]
    list_filter = ['brand', 'created_at']
    search_fields = ['name', 'brand']
    inlines = [ProductImageInline, StorageOptionInline, ColorOptionInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin cho model Review."""
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin cho model Coupon."""
    list_display = ['code', 'get_discount_display', 'is_active', 'expires_at']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code']
    
    def get_discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f"{obj.discount_value}%"
        else:
            return f"{obj.discount_value:,}đ"
    get_discount_display.short_description = 'Giảm giá'


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    """Admin cho model ShippingAddress."""
    list_display = ['user', 'full_name', 'phone', 'address', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['user__username', 'full_name', 'phone', 'address']


class OrderItemInline(admin.TabularInline):
    """Hiển thị sản phẩm trong đơn hàng inline."""
    model = OrderItem
    readonly_fields = ['product', 'storage', 'color', 'quantity', 'price', 'subtotal']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin cho model Order."""
    list_display = ['id', 'user', 'full_name', 'phone', 'status', 'payment_method', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'full_name', 'phone', 'address']
    inlines = [OrderItemInline]
    readonly_fields = ['user', 'full_name', 'phone', 'address', 'subtotal', 'discount_amount', 'coupon_code', 'total', 'note', 'payment_method', 'payment_status', 'created_at', 'updated_at']
    actions = ['mark_approved', 'mark_processing', 'mark_completed']
    
    def mark_approved(self, request, queryset):
        """Đánh dấu đơn hàng đã duyệt."""
        queryset.update(status='approved')
    mark_approved.short_description = 'Đánh dấu đã duyệt'
    
    def mark_processing(self, request, queryset):
        """Đánh dấu đơn hàng đang tiếp nhận."""
        queryset.update(status='processing')
    mark_processing.short_description = 'Đánh dấu tiếp nhận'
    
    def mark_completed(self, request, queryset):
        """Đánh dấu đơn hàng thành công."""
        queryset.update(status='completed')
    mark_completed.short_description = 'Đánh dấu thành công'


