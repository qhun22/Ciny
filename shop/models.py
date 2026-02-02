"""
Models for the phone shop application.
Các model cho ứng dụng bán điện thoại.

Models:
- Product: Sản phẩm điện thoại chính
- ProductImage: Hình ảnh chi tiết của sản phẩm
- StorageOption: Tùy chọn bộ nhớ và giá
- ColorOption: Tùy chọn màu sắc và hình ảnh
- Review: Đánh giá và bình luận của khách hàng
- Coupon: Mã giảm giá
"""

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Model mở rộng cho User để lưu thông tin bổ sung.
    Lưu số điện thoại của người dùng.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name="Người dùng"
    )
    phone_number = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        verbose_name="Số điện thoại"
    )
    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name="SĐT đã xác thực"
    )
    
    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"
    
    def __str__(self):
        return f"Profile của {self.user.username}"


# Signal to create UserProfile when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


class Product(models.Model):
    """
    Model đại diện cho sản phẩm điện thoại.
    Mỗi sản phẩm có một hình ảnh chính, mô tả, giá cả và các thông số kỹ thuật.
    """
    
    # Thông tin cơ bản
    brand = models.CharField(max_length=100, verbose_name="Hãng sản xuất")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    main_image = models.ImageField(upload_to='products/', verbose_name="Ảnh chính")
    
    # Mô tả và thông số
    description = models.TextField(verbose_name="Mô tả sản phẩm")
    specifications = models.TextField(verbose_name="Thông số kỹ thuật")
    
    # Giá cả
    original_price = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name="Giá gốc"
    )
    sale_price = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name="Giá khuyến mãi"
    )
    discount_percent = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        verbose_name="Phần trăm giảm giá (%)"
    )
    
    # Tồn kho
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Số lượng tồn kho"
    )
    
    # Thông tin bảo hành và đặc điểm
    warranty_months = models.PositiveIntegerField(
        default=12, 
        verbose_name="Thời gian bảo hành (tháng)"
    )
    free_shipping = models.BooleanField(default=False, verbose_name="Miễn phí vận chuyển")
    open_box_check = models.BooleanField(
        default=False, 
        verbose_name="Mở hộp kiểm tra"
    )
    return_30_days = models.BooleanField(
        default=False, 
        verbose_name="Đổi trả trong 30 ngày"
    )
    
    # Thời gian tạo
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    class Meta:
        # Sắp xếp theo ngày tạo mới nhất
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.brand} {self.name}"
    
    @property
    def discount_percent_display(self):
        """
        Tính phần trăm giảm giá tự động (hiển thị).
        Nếu giá khuyến mãi >= giá gốc thì trả về 0.
        """
        if self.sale_price >= self.original_price:
            return 0
        discount = self.original_price - self.sale_price
        return int((discount / self.original_price) * 100)
    
    @property
    def formatted_original_price(self):
        """Định dạng giá gốc theo đ."""
        return f"{int(self.original_price):,}đ"
    
    @property
    def formatted_sale_price(self):
        """Định dạng giá khuyến mãi theo đ."""
        return f"{int(self.sale_price):,}đ"


class ProductImage(models.Model):
    """
    Model cho hình ảnh chi tiết của sản phẩm.
    Mỗi sản phẩm có thể có nhiều hình ảnh (tối đa khoảng 10).
    """
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Sản phẩm"
    )
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Hình ảnh")
    
    class Meta:
        verbose_name = "Hình ảnh chi tiết"
        verbose_name_plural = "Hình ảnh chi tiết"
    
    def __str__(self):
        return f"Ảnh của {self.product.name}"


class StorageOption(models.Model):
    """
    Model cho tùy chọn bộ nhớ.
    Ví dụ: 128GB, 256GB, 512GB với giá gốc khác nhau.
    """
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='storage_options',
        verbose_name="Sản phẩm"
    )
    storage = models.CharField(max_length=50, verbose_name="Dung lượng bộ nhớ")
    original_price = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        default=0,
        verbose_name="Giá gốc"
    )
    
    class Meta:
        verbose_name = "Tùy chọn bộ nhớ"
        verbose_name_plural = "Tùy chọn bộ nhớ"
    
    def __str__(self):
        return f"{self.product.name} - {self.storage}"
    
    @property
    def sale_price(self):
        """Tính giá khuyến mãi dựa trên discount_percent của sản phẩm. Làm tròn về ngàn."""
        if self.product.discount_percent and float(self.product.discount_percent) > 0:
            discount = float(self.product.discount_percent)
            raw_price = float(self.original_price) * (100 - discount) / 100
            # Làm tròn về ngàn (chia 1000, làm tròn, nhân lại 1000)
            return int(round(raw_price / 1000) * 1000)
        return self.original_price


class ColorOption(models.Model):
    """
    Model cho tùy chọn màu sắc.
    Mỗi màu có một hình ảnh đại diện riêng.
    """
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='color_options',
        verbose_name="Sản phẩm"
    )
    color_name = models.CharField(max_length=50, verbose_name="Tên màu")
    color_image = models.ImageField(
        upload_to='products/colors/', 
        verbose_name="Hình ảnh màu"
    )
    
    class Meta:
        verbose_name = "Tùy chọn màu sắc"
        verbose_name_plural = "Tùy chọn màu sắc"
    
    def __str__(self):
        return f"{self.product.name} - {self.color_name}"


class Review(models.Model):
    """
    Model cho đánh giá và bình luận của khách hàng.
    Chỉ người dùng đã mua sản phẩm mới có thể đánh giá.
    """
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="Sản phẩm"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="Người dùng"
    )
    comment = models.TextField(verbose_name="Bình luận")
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name="Đánh giá ẩn danh"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đánh giá")
    
    class Meta:
        # Mỗi user chỉ được đánh giá một lần cho mỗi sản phẩm (mỗi lần mua)
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    def get_display_name(self):
        """Trả về tên hiển thị (có thể ẩn danh)."""
        if self.is_anonymous:
            # Hiển thị dạng: T*******
            username = self.user.username
            if len(username) >= 3:
                return username[:1] + '*' * (len(username) - 1)
            else:
                return '*' * len(username)
        return self.user.username
    
    def get_display_name_full(self):
        """Trả về tên đầy đủ hoặc ẩn danh."""
        if self.is_anonymous:
            return "Ẩn danh"
        return self.user.get_full_name() or self.user.username


class Coupon(models.Model):
    """
    Model cho mã giảm giá.
    Hỗ trợ giảm theo % hoặc số tiền cố định.
    """
    
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Giảm theo phần trăm'),
        ('fixed', 'Giảm số tiền cố định'),
    ]
    
    USAGE_TYPE_CHOICES = [
        ('all', 'Mọi người'),
        ('specific', 'Nhập email'),
    ]
    
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Mã giảm giá"
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name="Mô tả voucher"
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent',
        verbose_name="Loại giảm giá"
    )
    discount_value = models.PositiveIntegerField(
        default=0,
        verbose_name="Giá trị giảm"
    )
    min_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Đơn hàng tối thiểu (đ)"
    )
    max_usage = models.PositiveIntegerField(
        default=0,
        verbose_name="Số người sử dụng tối đa",
        help_text="0 = không giới hạn số người"
    )
    max_usage_per_user = models.PositiveIntegerField(
        default=1,
        verbose_name="Mỗi user sử dụng tối đa",
        help_text="Số lần mỗi user được sử dụng voucher này"
    )
    usage_type = models.CharField(
        max_length=10,
        choices=USAGE_TYPE_CHOICES,
        default='all',
        verbose_name="Ai có thể sử dụng"
    )
    specific_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email áp dụng",
        help_text="Nhập email người dùng được sử dụng voucher này"
    )
    is_active = models.BooleanField(default=True, verbose_name="Còn hiệu lực")
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Hết hạn"
    )
    max_product_limit = models.PositiveIntegerField(
        default=0,
        verbose_name="Sản phẩm tối đa cùng lúc",
        help_text="0 = không giới hạn. Ví dụ: set 1 thì chỉ áp dụng cho 1 sản phẩm, set 3 thì áp dụng cho tối đa 3 sản phẩm."
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Đã sử dụng",
        help_text="Số lần voucher đã được sử dụng trong đơn hàng"
    )
    
    class Meta:
        verbose_name = "Mã giảm giá"
        verbose_name_plural = "Mã giảm giá"
    
    def __str__(self):
        if self.discount_type == 'percent':
            return f"{self.code} - {self.discount_value}% OFF"
        else:
            return f"{self.code} - {self.discount_value:,}đ OFF"
    
    def calculate_discount(self, total_amount):
        """Tính số tiền giảm giá."""
        if not self.is_active:
            return 0
        
        # Kiểm tra đơn hàng tối thiểu
        if self.min_order > 0 and total_amount < self.min_order:
            return 0
        
        if self.discount_type == 'percent':
            discount = total_amount * self.discount_value / 100
            return int(discount)
        else:
            # Giảm cố định, không vượt quá tổng tiền
            return min(self.discount_value, total_amount)


class UserVoucher(models.Model):
    """
    Model cho voucher của từng user.
    Mỗi user có thể có nhiều voucher.
    Voucher tự động xóa khi hết hạn.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_vouchers',
        verbose_name="Người dùng"
    )
    coupon = models.ForeignKey(
        'Coupon',
        on_delete=models.CASCADE,
        related_name='user_vouchers',
        verbose_name="Mã giảm giá"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày nhận")
    is_used = models.BooleanField(default=False, verbose_name="Đã sử dụng")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày sử dụng")
    order = models.ForeignKey(
        'Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_vouchers',
        verbose_name="Đơn hàng sử dụng"
    )

    class Meta:
        verbose_name = "Voucher của user"
        verbose_name_plural = "Voucher của user"

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"


class ShippingAddress(models.Model):
    """
    Model cho địa chỉ giao hàng của người dùng.
    Mỗi user có thể có nhiều địa chỉ.
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='shipping_addresses',
        verbose_name="Người dùng"
    )
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ")
    is_default = models.BooleanField(default=False, verbose_name="Địa chỉ mặc định")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    class Meta:
        verbose_name = "Địa chỉ giao hàng"
        verbose_name_plural = "Địa chỉ giao hàng"
    
    def __str__(self):
        return f"{self.full_name} - {self.address[:50]}..."


class Cart(models.Model):
    """
    Model cho giỏ hàng.
    Mỗi user (hoặc session) có một giỏ hàng.
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cart',
        verbose_name="Người dùng",
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=255, 
        verbose_name="Session key",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"
    
    def __str__(self):
        if self.user:
            return f"Giỏ hàng của {self.user.username}"
        return f"Giỏ hàng (session)"
    
    @property
    def total_items(self):
        """Tổng số sản phẩm trong giỏ."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Tổng tiền."""
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """
    Model cho sản phẩm trong giỏ hàng.
    """
    
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Giỏ hàng"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='cart_items',
        verbose_name="Sản phẩm"
    )
    storage = models.CharField(max_length=50, verbose_name="Bộ nhớ", blank=True)
    color = models.CharField(max_length=50, verbose_name="Màu sắc", blank=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name="Giá tại thời điểm thêm"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày thêm")
    
    class Meta:
        verbose_name = "Sản phẩm trong giỏ hàng"
        verbose_name_plural = "Sản phẩm trong giỏ hàng"
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.price}"
    
    @property
    def subtotal(self):
        """Thành tiền."""
        return self.price * self.quantity


class Order(models.Model):
    """
    Model cho đơn hàng.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('processing', 'Tiếp nhận'),
        ('completed', 'Thành công'),
        ('cancelled', 'Đã hủy'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng (COD)'),
        ('online', 'Thanh toán online'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name="Khách hàng"
    )
    
    # Thông tin người nhận
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên người nhận")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ giao hàng")
    
    # Thông tin đơn hàng
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="Trạng thái"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod',
        verbose_name="Phương thức thanh toán"
    )
    payment_status = models.CharField(
        max_length=20,
        default='unpaid',
        verbose_name="Trạng thái thanh toán"
    )
    
    # Tiền tệ
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Tổng tiền hàng"
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="Giảm giá"
    )
    coupon_code = models.CharField(max_length=50, blank=True, verbose_name="Mã giảm giá")
    total = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Tổng thanh toán"
    )
    
    # Ghi chú
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt hàng")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    """
    Model cho sản phẩm trong đơn hàng.
    """
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Đơn hàng"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='order_items',
        verbose_name="Sản phẩm"
    )
    product_name = models.CharField(max_length=300, verbose_name="Tên sản phẩm")
    storage = models.CharField(max_length=50, verbose_name="Bộ nhớ", blank=True)
    color = models.CharField(max_length=50, verbose_name="Màu sắc", blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name="Giá"
    )
    is_reviewed = models.BooleanField(default=False, verbose_name="Đã đánh giá")
    
    class Meta:
        verbose_name = "Sản phẩm trong đơn hàng"
        verbose_name_plural = "Sản phẩm trong đơn hàng"
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    @property
    def subtotal(self):
        """Thành tiền."""
        return self.price * self.quantity


class Feedback(models.Model):
    """
    Model cho góp ý của khách hàng.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name="Người gửi"
    )
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    content = models.TextField(verbose_name="Nội dung")
    admin_response = models.TextField(blank=True, null=True, verbose_name="Phản hồi từ admin")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày gửi")
    responded_at = models.DateTimeField(blank=True, null=True, verbose_name="Ngày phản hồi")
    
    class Meta:
        verbose_name = "Góp ý"
        verbose_name_plural = "Góp ý"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @property
    def is_responded(self):
        """Kiểm tra đã được phản hồi chưa."""
        return bool(self.admin_response)

