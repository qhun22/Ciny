"""
Views for the phone shop application.
Các view cho ứng dụng bán điện thoại.

Các view sử dụng function-based views để dễ hiểu cho sinh viên.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Product, Review, Coupon, ProductImage, StorageOption, ColorOption, Cart, CartItem, ShippingAddress, Order, OrderItem, UserProfile, UserVoucher, Feedback
from .forms import RegistrationForm, ReviewForm, CouponForm


def home(request):
    """
    Trang chủ - Hiển thị danh sách sản phẩm.
    Mỗi sản phẩm hiển thị: ảnh chính, tên, giá gốc (gạch ngang), giá khuyến mãi, phần trăm giảm giá.
    """
    # Lấy tối đa 15 sản phẩm, sắp xếp theo ngày tạo mới nhất
    products = Product.objects.all().order_by('-created_at')[:15]

    # Lấy sản phẩm khuyến mãi đặc biệt (có giảm giá)
    special_promotions = []
    show_promotion = False

    # Lấy tối đa 5 sản phẩm có discount_percent > 0
    promoted_products = Product.objects.filter(discount_percent__gt=0).order_by('-discount_percent')[:5]

    if promoted_products.exists():
        show_promotion = True
        for product in promoted_products:
            # Tính giá sau giảm
            discounted_price = int(product.original_price * (100 - product.discount_percent) / 100)
            special_promotions.append({
                'product': product,
                'discount_percent': int(product.discount_percent),
                'discounted_price': discounted_price,
            })

    context = {
        'products': products,
        'show_promotion': show_promotion,
        'special_promotions': special_promotions,
        'page_title': 'Trang chủ - Cửa hàng điện thoại',
    }

    return render(request, 'home/index.html', context)


def product_search(request):
    """
    Trang tìm kiếm sản phẩm.
    Tìm kiếm theo tên, hãng, mô tả.
    """
    query = request.GET.get('q', '').strip()

    if not query:
        products = Product.objects.all()[:12]  # Hiển thị 12 sản phẩm mặc định
    else:
        # Tìm kiếm theo tên, hãng hoặc mô tả
        products = Product.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(brand__icontains=query) |
            models.Q(description__icontains=query)
        ).distinct()

    context = {
        'products': products,
        'query': query,
        'page_title': f'Tìm kiếm: {query} - PhoneShop' if query else 'Tìm kiếm sản phẩm',
    }

    return render(request, 'home/index.html', context)


def product_detail(request, product_id):
    """
    Trang chi tiết sản phẩm.
    Hiển thị:
    - Gallery hình ảnh
    - Thông tin sản phẩm (tên, giá, giảm giá, thông số kỹ thuật, mô tả)
    - Tùy chọn bộ nhớ và màu sắc
    - Video YouTube (nếu có)
    - Mã giảm giá
    - Đánh giá của khách hàng
    """
    # Lấy sản phẩm theo ID, nếu không có trả về 404
    product = get_object_or_404(Product, id=product_id)
    
    # Lấy tất cả đánh giá của sản phẩm này
    reviews = product.reviews.all()
    
    # Xử lý form đánh giá (chỉ khi user đã đăng nhập VÀ đã mua sản phẩm)
    review_form = None
    can_review = False
    has_purchased = False
    
    if request.user.is_authenticated:
        # Kiểm tra xem user đã mua sản phẩm này chưa (đơn hàng đã hoàn thành)
        user_completed_orders = Order.objects.filter(
            user=request.user,
            status='completed'
        ).prefetch_related('items')
        
        # Tìm các order items chưa được đánh giá
        purchasable_items = []
        for order in user_completed_orders:
            for item in order.items.all():
                if item.product and item.product.id == product_id and not item.is_reviewed:
                    purchasable_items.append(item)
        
        has_purchased = len(purchasable_items) > 0
        
        # Kiểm tra xem user có thể đánh giá không (đã mua và chưa đánh giá)
        if has_purchased:
            # Kiểm tra user đã đánh giá sản phẩm này chưa
            user_has_reviewed = reviews.filter(user=request.user).exists()
            if not user_has_reviewed:
                review_form = ReviewForm()
                can_review = True
    
    # Xử lý form mã giảm giá
    coupon_form = CouponForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'coupon_form': coupon_form,
        'can_review': can_review,
        'has_purchased': has_purchased,
        'page_title': f'{product.brand} {product.name} - Chi tiết sản phẩm',
    }
    
    return render(request, 'product/detail.html', context)


@require_POST
def add_review(request, product_id):
    """
    Xử lý thêm đánh giá mới cho sản phẩm.
    Chỉ user đã đăng nhập VÀ đã mua sản phẩm mới có thể đánh giá.
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Kiểm tra user đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để đánh giá sản phẩm.')
        return redirect('product_detail', product_id=product_id)
    
    # Kiểm tra user đã mua sản phẩm này chưa (đơn hàng đã hoàn thành và chưa đánh giá)
    user_completed_orders = Order.objects.filter(
        user=request.user,
        status='completed'
    ).prefetch_related('items')
    
    purchasable_items = []
    for order in user_completed_orders:
        for item in order.items.all():
            if item.product and item.product.id == product_id and not item.is_reviewed:
                purchasable_items.append(item)
    
    if not purchasable_items:
        messages.error(request, 'Bạn cần mua sản phẩm này trước khi đánh giá.')
        return redirect('product_detail', product_id=product_id)
    
    # Kiểm tra user đã đánh giá sản phẩm này chưa
    if product.reviews.filter(user=request.user).exists():
        messages.warning(request, 'Bạn đã đánh giá sản phẩm này rồi.')
        return redirect('product_detail', product_id=product_id)
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        # Xử lý checkbox is_anonymous
        review.is_anonymous = 'is_anonymous' in request.POST
        review.save()
        
        # Đánh dấu một order item là đã đánh giá
        # (mỗi lần mua chỉ được đánh giá 1 lần)
        if purchasable_items:
            purchasable_items[0].is_reviewed = True
            purchasable_items[0].save()
        
        messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
    else:
        messages.error(request, 'Vui lòng nhập đầy đủ thông tin đánh giá.')
    
    return redirect('product_detail', product_id=product_id)


@require_POST
def apply_coupon(request, product_id):
    """
    Xử lý áp dụng mã giảm giá.
    Trả về JSON response với thông tin mã giảm giá.
    """
    product = get_object_or_404(Product, id=product_id)
    form = CouponForm(request.POST)
    
    if form.is_valid():
        code = form.cleaned_data['code']
        coupon = Coupon.objects.get(code=code, is_active=True)
        
        # Tính giá sau khi giảm
        discount_amount = product.sale_price * coupon.percent_discount / 100
        final_price = product.sale_price - discount_amount
        
        return JsonResponse({
            'success': True,
            'message': f'Áp dụng mã {code} thành công! Giảm {coupon.percent_discount}%.',
            'discount_percent': coupon.percent_discount,
            'final_price': str(int(final_price)),
        })
    else:
        return JsonResponse({
            'success': False,
            'message': form.errors['code'][0],
        })


def login_view(request):
    """
    Trang đăng nhập.
    Sử dụng email hoặc số điện thoại để đăng nhập.
    """
    # Nếu user đã đăng nhập thì chuyển về trang chủ
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Xử lý form đăng nhập với email hoặc số điện thoại
        from django.contrib.auth import authenticate, login
        email_or_phone = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not email_or_phone or not password:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
        else:
            user = None

            # Thử tìm theo email trước
            if '@' in email_or_phone:
                user = User.objects.filter(email=email_or_phone).first()
                if user:
                    user = authenticate(request, username=user.username, password=password)
            else:
                # Tìm theo username (số điện thoại)
                user = authenticate(request, username=email_or_phone, password=password)

            if user is not None:
                login(request, user)
                # Hiển thị chào họ và tên
                display_name = user.first_name if user.first_name else user.email.split('@')[0]
                messages.success(request, f'Xin chào, {display_name}!')

                # Chuyển hướng về trang trước đó hoặc trang chủ
                next_page = request.GET.get('next', '/')
                return redirect(next_page)
            else:
                messages.error(request, 'Email/số điện thoại hoặc mật khẩu không đúng.')

    context = {
        'page_title': 'Đăng nhập',
    }
    return render(request, 'auth/login.html', context)


def register_view(request):
    """
    Trang đăng ký tài khoản mới.
    Sử dụng email làm username để đăng nhập.
    """
    # Nếu user đã đăng nhập thì chuyển về trang chủ
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Tạo user mới (form.save với commit=False để kiểm soát việc save)
            user = form.save(commit=False)
            
            # Lưu user vào database (signal sẽ tạo UserProfile)
            user.save()

            # Đăng nhập user ngay sau khi đăng ký
            from django.contrib.auth import login
            login(request, user)

            messages.success(request, 'Đăng ký tài khoản thành công! Xin chào, {}!'.format(user.first_name))
            return redirect('home')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
        'page_title': 'Đăng ký tài khoản',
    }
    return render(request, 'auth/register.html', context)


def forgot_password_view(request):
    """
    Trang quên mật khẩu.
    Đặt lại mật khẩu về 12345.
    """
    # Nếu user đã đăng nhập thì chuyển về trang chủ
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email_or_phone = request.POST.get('email_or_phone', '').strip()

        if not email_or_phone:
            messages.error(request, 'Vui lòng nhập email hoặc số điện thoại.')
        else:
            # Tìm user theo email hoặc username
            from django.contrib.auth.models import User
            user = None

            # Thử tìm theo email trước
            if '@' in email_or_phone:
                user = User.objects.filter(email=email_or_phone).first()
            else:
                # Tìm theo username (số điện thoại cũng là username)
                user = User.objects.filter(username=email_or_phone).first()

            if user:
                # Đặt lại mật khẩu về 12345
                user.set_password('12345')
                user.save()
                messages.success(request, f'Mật khẩu của tài khoản "{user.username}" đã được đặt lại về 12345. Vui lòng đăng nhập và đổi mật khẩu mới.')
                return redirect('login')
            else:
                messages.error(request, 'Không tìm thấy tài khoản với email hoặc số điện thoại này.')

    context = {
        'page_title': 'Quên mật khẩu',
    }
    return render(request, 'auth/forgot_password.html', context)


def logout_view(request):
    """
    Xử lý đăng xuất.
    """
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất thành công.')
    return redirect('home')


def is_admin(user):
    """
    Hàm kiểm tra user có phải là admin không.
    Sử dụng cho @user_passes_test decorator.
    """
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def admin_add_product(request):
    """
    Trang thêm sản phẩm mới (chỉ admin mới có thể truy cập).
    Cho phép:
    - Nhập thông tin cơ bản của sản phẩm
    - Upload ảnh chính
    - Upload nhiều ảnh chi tiết
    - Thêm nhiều tùy chọn bộ nhớ (dynamic)
    - Thêm nhiều tùy chọn màu sắc (dynamic)
    """
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        brand = request.POST.get('brand')
        name = request.POST.get('name')
        main_image = request.FILES.get('main_image')
        description = request.POST.get('description')
        specifications = request.POST.get('specifications')
        original_price = request.POST.get('original_price')
        discount_percent = request.POST.get('discount_percent', 0)
        
        # Tính giá khuyến mãi tự động
        original_price_val = int(original_price)
        discount_percent_val = float(discount_percent)
        sale_price_val = int(original_price_val * (100 - discount_percent_val) / 100)
        
        # Các trường còn lại
        warranty_months = request.POST.get('warranty_months', 12)
        stock_quantity = int(request.POST.get('stock_quantity', 0))
        free_shipping = 'free_shipping' in request.POST
        open_box_check = 'open_box_check' in request.POST
        return_30_days = 'return_30_days' in request.POST
        
        # Tạo sản phẩm mới
        product = Product.objects.create(
            brand=brand,
            name=name,
            main_image=main_image,
            description=description,
            specifications=specifications,
            original_price=original_price_val,
            sale_price=sale_price_val,
            discount_percent=discount_percent_val,
            warranty_months=warranty_months,
            stock_quantity=stock_quantity,
            free_shipping=free_shipping,
            open_box_check=open_box_check,
            return_30_days=return_30_days,
        )
        
        # Thêm hình ảnh chi tiết
        detail_images = request.FILES.getlist('detail_images')
        for image in detail_images:
            if image:
                ProductImage.objects.create(product=product, image=image)
        
        # Thêm tùy chọn bộ nhớ (với giá gốc)
        storage_names = request.POST.getlist('storage_name[]')
        storage_prices = request.POST.getlist('storage_price[]')
        for i in range(len(storage_names)):
            if storage_names[i].strip():
                StorageOption.objects.create(
                    product=product,
                    storage=storage_names[i],
                    original_price=storage_prices[i] if i < len(storage_prices) else 0,
                )
        
        # Thêm tùy chọn màu sắc
        color_names = request.POST.getlist('color_name[]')
        color_images = request.FILES.getlist('color_image[]')
        for i in range(len(color_names)):
            if color_names[i].strip() and i < len(color_images):
                if color_images[i]:
                    ColorOption.objects.create(
                        product=product,
                        color_name=color_names[i],
                        color_image=color_images[i],
                    )
        
        messages.success(request, f'Đã thêm sản phẩm "{product.name}" thành công!')
        return redirect('admin_product_list')
    
    context = {
        'page_title': 'Thêm sản phẩm mới - Admin',
    }
    return render(request, 'admin/add_product.html', context)


# Import models để dùng aggregate
from django.db import models


def profile_view(request):
    """
    Trang profile của người dùng.
    Hiển thị thông tin tài khoản, địa chỉ giao hàng và nút truy cập trang quản trị (nếu là admin).
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Vui lòng đăng nhập để xem profile.')
        return redirect('login')
    
    user = request.user
    
    # Xử lý POST request (cập nhật thông tin)
    if request.method == 'POST':
        from django.contrib.auth import update_session_auth_hash
        
        # Cập nhật họ tên
        full_name = request.POST.get('full_name', '').strip()
        if full_name:
            user.first_name = full_name
            user.save()
        
        # Cập nhật số điện thoại (chỉ khi chưa được xác thực)
        phone_number = request.POST.get('phone_number', '').strip()
        is_phone_verified = getattr(user.profile, 'is_phone_verified', False)
        
        if phone_number and not is_phone_verified:
            # KIỂM TRA: Số điện thoại đã được sử dụng chưa?
            phone_exists = UserProfile.objects.filter(
                phone_number=phone_number,
                is_phone_verified=True
            ).exclude(user=user).exists()
            
            if phone_exists:
                messages.error(request, 'Số điện thoại này đã được sử dụng bởi tài khoản khác!')
            else:
                try:
                    user.profile.phone_number = phone_number
                    user.profile.is_phone_verified = True  # Khóa số điện thoại sau khi cập nhật
                    user.profile.save()
                    messages.success(request, 'Cập nhật số điện thoại thành công! Số điện thoại đã được khóa.')
                    
                    # Tặng voucher QHUN22 cho user khi xác thực số điện thoại
                    try:
                        qhun22_coupon = Coupon.objects.get(code='QHUN22', is_active=True)
                        
                        # Kiểm tra xem user đã có voucher này chưa
                        existing_user_voucher = UserVoucher.objects.filter(
                            user=user,
                            coupon=qhun22_coupon
                        ).exists()
                        
                        if not existing_user_voucher:
                            UserVoucher.objects.create(
                                user=user,
                                coupon=qhun22_coupon
                            )
                            messages.success(request, 'Chúc mừng! Bạn đã nhận được voucher QHUN22!')
                    except Coupon.DoesNotExist:
                        pass  # Voucher QHUN22 không tồn tại, bỏ qua
                        
                except Exception as e:
                    messages.error(request, 'Có lỗi xảy ra. Vui lòng thử lại.')
        
        # Đổi mật khẩu
        old_password = request.POST.get('old_password', '').strip()
        new_password1 = request.POST.get('new_password1', '').strip()
        new_password2 = request.POST.get('new_password2', '').strip()
        
        if old_password or new_password1 or new_password2:
            if not old_password:
                messages.error(request, 'Vui lòng nhập mật khẩu hiện tại.')
            elif not new_password1:
                messages.error(request, 'Vui lòng nhập mật khẩu mới.')
            elif new_password1 != new_password2:
                messages.error(request, 'Mật khẩu mới không khớp.')
            elif len(new_password1) < 6:
                messages.error(request, 'Mật khẩu mới phải có ít nhất 6 ký tự.')
            else:
                # Kiểm tra mật khẩu cũ
                if user.check_password(old_password):
                    user.set_password(new_password1)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Đổi mật khẩu thành công!')
                else:
                    messages.error(request, 'Mật khẩu hiện tại không đúng.')
        elif full_name or (phone_number and not is_phone_verified):
            messages.success(request, 'Cập nhật thông tin thành công!')
    
    # Kiểm tra user có phải admin không
    is_admin_user = request.user.is_staff or request.user.is_superuser
    
    # Lấy số lượng đánh giá của user
    user_reviews_count = request.user.reviews.count()
    
    # Lấy danh sách địa chỉ của user
    addresses = request.user.shipping_addresses.all().order_by('-is_default', '-created_at')
    
    # Lấy số điện thoại và trạng thái xác thực từ UserProfile
    try:
        if hasattr(request.user, 'profile'):
            phone_number = request.user.profile.phone_number
            is_phone_verified = getattr(request.user.profile, 'is_phone_verified', False)
        else:
            phone_number = None
            is_phone_verified = False
    except:
        phone_number = None
        is_phone_verified = False
    
    # Xác định tab active
    active_tab = request.GET.get('tab', '')
    
    # Lấy danh sách voucher của user (chỉ lấy voucher còn hạn, active và CHƯA sử dụng)
    from django.utils import timezone
    vouchers = UserVoucher.objects.filter(
        user=request.user,
        coupon__is_active=True,
        is_used=False  # Chỉ lấy voucher chưa sử dụng
    ).filter(
        models.Q(coupon__expires_at__isnull=True) | 
        models.Q(coupon__expires_at__gt=timezone.now())
    ).select_related('coupon').order_by('-created_at')
    
    # Lấy danh sách đơn hàng của user (prefetech items và product để hiển thị ảnh)
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    
    # Lấy danh sách góp ý của user
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'user': request.user,
        'is_admin': is_admin_user,
        'reviews_count': user_reviews_count,
        'addresses': addresses,
        'phone_number': phone_number,
        'is_phone_verified': is_phone_verified,
        'active_tab': active_tab,
        'user_vouchers': vouchers,
        'orders': orders,
        'feedbacks': feedbacks,
        'page_title': f'Profile - {request.user.username}',
    }
    
    return render(request, 'auth/profile.html', context)


@require_POST
def address_add(request):
    """
    Thêm địa chỉ giao hàng mới.
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Vui lòng đăng nhập.')
        return redirect('login')
    
    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    
    if not full_name or not phone or not address:
        messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
        return redirect('profile')
    
    # Nếu đánh dấu là mặc định, bỏ chọn địa chỉ mặc định cũ
    if 'is_default' in request.POST:
        ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    ShippingAddress.objects.create(
        user=request.user,
        full_name=full_name,
        phone=phone,
        address=address,
        is_default='is_default' in request.POST
    )
    
    messages.success(request, 'Đã thêm địa chỉ mới.')
    return redirect('profile')


@require_POST
def address_set_default(request):
    """
    Đặt địa chỉ mặc định từ form chọn nhiều địa chỉ.
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Vui lòng đăng nhập.')
        return redirect('login')
    
    default_address_id = request.POST.get('default_address')
    
    if default_address_id:
        try:
            address_id = int(default_address_id)
            # Bỏ đánh dấu địa chỉ mặc định cũ
            ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
            # Đặt địa chỉ mới làm mặc định
            address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
            address.is_default = True
            address.save()
            messages.success(request, 'Đã cập nhật địa chỉ mặc định.')
        except (ShippingAddress.DoesNotExist, ValueError):
            messages.error(request, 'Địa chỉ không hợp lệ.')
    else:
        messages.warning(request, 'Vui lòng chọn địa chỉ mặc định.')
    
    return HttpResponseRedirect(reverse('profile') + '?tab=addresses')


@require_POST
def address_set_default_post(request):
    """
    Đặt địa chỉ mặc định từ form POST (dùng cho profile page).
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Vui lòng đăng nhập.')
        return redirect('login')
    
    default_address_id = request.POST.get('default_address')
    
    if default_address_id:
        try:
            address_id = int(default_address_id)
            # Bỏ đánh dấu địa chỉ mặc định cũ
            ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
            # Đặt địa chỉ mới làm mặc định
            address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
            address.is_default = True
            address.save()
            messages.success(request, 'Đã cập nhật địa chỉ mặc định.')
        except (ShippingAddress.DoesNotExist, ValueError):
            messages.error(request, 'Địa chỉ không hợp lệ.')
    else:
        messages.warning(request, 'Vui lòng chọn địa chỉ mặc định.')
    
    return HttpResponseRedirect('/profile/?tab=addresses')


@require_POST
def address_delete(request, address_id):
    """
    Xóa địa chỉ giao hàng.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    
    messages.success(request, 'Đã xóa địa chỉ.')
    return redirect('profile')


@require_POST
def voucher_delete(request):
    """
    Xóa voucher đã chọn của user.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    voucher_ids = request.POST.getlist('voucher_ids')
    
    if voucher_ids:
        # Chỉ xóa voucher thuộc về user hiện tại
        UserVoucher.objects.filter(id__in=voucher_ids, user=request.user).delete()
        messages.success(request, f'Đã xóa {len(voucher_ids)} voucher.')
    else:
        messages.warning(request, 'Vui lòng chọn voucher cần xóa.')
    
    return HttpResponseRedirect(reverse('profile') + '?tab=vouchers')


@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Trang admin chinh thuc (Dashboard quan ly - qhun22.html).
    Hien thi thong ke va quan ly cua hang.
    """
    # Thong ke tong quan
    total_products = Product.objects.count()
    total_users = User.objects.count()
    total_reviews = Review.objects.count()
    total_coupons = Coupon.objects.count()
    total_orders = Order.objects.count()
    
    # Tong doanh thu (chi don hang thanh cong)
    total_revenue = Order.objects.filter(status='completed').aggregate(
        total=models.Sum('total')
    )['total'] or 0
    
    # Thong ke theo thang hien tai
    from django.utils import timezone
    now = timezone.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Nguoi dung moi thang nay
    monthly_new_users = User.objects.filter(date_joined__gte=first_day_of_month).count()
    
    # Don hang thang nay
    monthly_orders = Order.objects.filter(created_at__gte=first_day_of_month).count()
    
    # Doanh thu thang nay (chi don hang thanh cong)
    monthly_revenue = Order.objects.filter(
        status='completed',
        created_at__gte=first_day_of_month
    ).aggregate(total=models.Sum('total'))['total'] or 0
    
    # San pham gan day
    recent_products = Product.objects.all().order_by('-created_at')[:5]
    
    # Don hang gan day
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_reviews': total_reviews,
        'total_coupons': total_coupons,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'monthly_new_users': monthly_new_users,
        'monthly_orders': monthly_orders,
        'monthly_revenue': monthly_revenue,
        'recent_products': recent_products,
        'recent_orders': recent_orders,
        'page_title': 'Trang quan tri - PhoneShop',
    }
    
    return render(request, 'admin/qhun22.html', context)


@user_passes_test(is_admin)
def admin_product_list(request):
    """
    Trang danh sách tất cả sản phẩm (quản lý).
    Admin có thể xem, chỉnh sửa và xóa sản phẩm.
    """
    products = Product.objects.all().order_by('-created_at')
    
    context = {
        'products': products,
        'page_title': 'Quan ly san pham - Admin',
    }
    
    return render(request, 'admin/product_list.html', context)


@user_passes_test(is_admin)
def admin_edit_product(request, product_id):
    """
    Trang chỉnh sửa sản phẩm (chỉ admin).
    Hiển thị thông tin hiện có và cho phép cập nhật.
    """
    import os
    from django.conf import settings
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Lay du lieu tu form
        product.brand = request.POST.get('brand')
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.specifications = request.POST.get('specifications')
        
        # Tinh toan gia moi
        original_price = int(request.POST.get('original_price', 0))
        discount_percent = float(request.POST.get('discount_percent', 0))
        sale_price = int(original_price * (100 - discount_percent) / 100)
        
        product.original_price = original_price
        product.sale_price = sale_price
        product.discount_percent = discount_percent
        product.warranty_months = request.POST.get('warranty_months', 12)
        product.stock_quantity = int(request.POST.get('stock_quantity', 0))
        
        # Checkbox values
        product.free_shipping = 'free_shipping' in request.POST
        product.open_box_check = 'open_box_check' in request.POST
        product.return_30_days = 'return_30_days' in request.POST
        
        # Xoa anh chinh neu duoc danh dau
        delete_main_image = request.POST.get('delete_main_image') == 'true'
        if delete_main_image:
            # Xoa file cu
            if product.main_image:
                try:
                    old_path = os.path.join(settings.MEDIA_ROOT, str(product.main_image))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except:
                    pass
            product.main_image = None
        
        # Upload anh chinh moi neu co
        new_main_image = request.FILES.get('main_image')
        if new_main_image:
            # Xoa file cu neu co
            if product.main_image:
                try:
                    old_path = os.path.join(settings.MEDIA_ROOT, str(product.main_image))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except:
                    pass
            product.main_image = new_main_image
        
        product.save()
        
        # Xoa anh chi tiet duoc danh dau
        delete_images_str = request.POST.get('delete_images', '').strip()
        if delete_images_str:
            delete_image_ids = [int(x) for x in delete_images_str.split(',') if x]
            for img_id in delete_image_ids:
                try:
                    img = ProductImage.objects.get(id=img_id, product=product)
                    # Xoa file
                    if img.image:
                        try:
                            img_path = os.path.join(settings.MEDIA_ROOT, str(img.image))
                            if os.path.exists(img_path):
                                os.remove(img_path)
                        except:
                            pass
                    img.delete()
                except ProductImage.DoesNotExist:
                    pass
        
        # Xu ly anh chi tiet moi
        new_detail_images = request.FILES.getlist('detail_images')
        for image in new_detail_images:
            if image:
                ProductImage.objects.create(product=product, image=image)
        
        # Xoa storage duoc danh dau
        delete_storages_str = request.POST.get('delete_storages', '').strip()
        if delete_storages_str:
            delete_storage_ids = [int(x) for x in delete_storages_str.split(',') if x]
            StorageOption.objects.filter(id__in=delete_storage_ids, product=product).delete()
        
        # Xoa color duoc danh dau
        delete_colors_str = request.POST.get('delete_colors', '').strip()
        if delete_colors_str:
            delete_color_ids = [int(x) for x in delete_colors_str.split(',') if x]
            for color_id in delete_color_ids:
                try:
                    color = ColorOption.objects.get(id=color_id, product=product)
                    # Xoa file anh mau
                    if color.color_image:
                        try:
                            color_path = os.path.join(settings.MEDIA_ROOT, str(color.color_image))
                            if os.path.exists(color_path):
                                os.remove(color_path)
                        except:
                            pass
                    color.delete()
                except ColorOption.DoesNotExist:
                    pass
        
        # Lay danh sach ID cua storage bi danh dau xoa
        delete_storages_str = request.POST.get('delete_storages', '').strip()
        deleted_storage_ids = [int(x) for x in delete_storages_str.split(',')] if delete_storages_str else []
        
        # Xoa storage danh dau xoa
        if deleted_storage_ids:
            StorageOption.objects.filter(id__in=deleted_storage_ids, product=product).delete()
        
        # Them storage moi tu form (chi nhung dong co ten)
        storage_names = request.POST.getlist('storage_name[]')
        storage_prices = request.POST.getlist('storage_price[]')
        for i in range(len(storage_names)):
            if storage_names[i].strip():
                StorageOption.objects.create(
                    product=product,
                    storage=storage_names[i],
                    original_price=storage_prices[i] if i < len(storage_prices) else 0,
                )
        
        # Lay danh sach ID cua color bi danh dau xoa
        deleted_color_ids = [int(x) for x in delete_colors_str.split(',')] if delete_colors_str else []
        
        # Them color moi tu form (chi nhung dong co ten)
        color_names = request.POST.getlist('color_name[]')
        color_images = request.FILES.getlist('color_image[]')
        for i in range(len(color_names)):
            if color_names[i].strip():
                ColorOption.objects.create(
                    product=product,
                    color_name=color_names[i],
                    color_image=color_images[i] if i < len(color_images) and color_images[i] else None,
                )
        
        messages.success(request, f"Da cap nhat san pham \"{product.name}\" thanh cong!")
        return redirect('admin_edit_product', product_id=product.id)
    
    context = {
        'product': product,
        'page_title': f'Chinh sua - {product.brand} {product.name}',
        'is_edit': True,
    }
    
    return render(request, 'admin/edit_product.html', context)


@user_passes_test(is_admin)
@require_POST
def admin_delete_product(request, product_id):
    """
    Xoa san pham (chi admin).
    Xoa ca cac file anh trong storage.
    """
    import os
    from django.conf import settings
    
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    
    print(f"===== Dang xoa san pham: {product_name} (ID: {product_id}) =====")
    
    # Xoa file anh chinh
    if product.main_image:
        try:
            main_image_path = os.path.join(settings.MEDIA_ROOT, str(product.main_image))
            print(f"Xoa anh chinh: {main_image_path}")
            if os.path.exists(main_image_path):
                os.remove(main_image_path)
                print(f"  -> Da xoa anh chinh")
            else:
                print(f"  -> Khong tim thay file: {main_image_path}")
        except Exception as e:
            print(f"Loi xoa anh chinh: {e}")
    
    # Xoa cac anh chi tiet va file
    print(f"Xoa anh chi tiet (gallery)...")
    for img in product.images.all():
        if img.image:
            try:
                img_path = os.path.join(settings.MEDIA_ROOT, str(img.image))
                print(f"  Xoa: {img_path}")
                if os.path.exists(img_path):
                    os.remove(img_path)
                    print(f"    -> Da xoa")
                else:
                    print(f"    -> Khong tim thay file")
            except Exception as e:
                print(f"Loi xoa anh chi tiet {img.id}: {e}")
    
    # Xoa cac anh mau sac va file
    print(f"Xoa anh mau sac...")
    for color in product.color_options.all():
        if color.color_image:
            try:
                color_path = os.path.join(settings.MEDIA_ROOT, str(color.color_image))
                print(f"  Mau: {color.color_name} - File: {color_path}")
                if os.path.exists(color_path):
                    os.remove(color_path)
                    print(f"    -> Da xoa")
                else:
                    print(f"    -> Khong tim thay file")
            except Exception as e:
                print(f"Loi xoa anh mau {color.id}: {e}")
    
    # Xoa cac ban ghi lien quan
    print(f"Xoa ban ghi database...")
    product.images.all().delete()
    product.storage_options.all().delete()
    product.color_options.all().delete()
    product.reviews.all().delete()
    print(f"  -> Da xoa images, storage_options, color_options, reviews")
    
    # Xoa san pham
    product.delete()
    print(f"  -> Da xoa san pham")
    
    messages.success(request, f'Da xoa san pham "{product_name}" thanh cong!')
    return redirect('admin_product_list')


# =====================
# GIỎ HÀNG (CART)
# =====================

def get_or_create_cart(request):
    """
    Lấy hoặc tạo giỏ hàng cho user hiện tại.
    Hỗ cả user đã đăng nhập và guest (session).
    """
    if request.user.is_authenticated:
        # User đã đăng nhập - dùng user object
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Xóa cart theo session nếu có
        if request.session.get('cart_session_key'):
            Cart.objects.filter(session_key=request.session['cart_session_key']).delete()
    else:
        # Guest - dùng session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    return cart


def cart_detail(request):
    """
    Trang xem giỏ hàng.
    Mỗi lần vào trang giỏ hàng, luôn bắt đầu với trạng thái TRỐNG (không coupon).
    """
    cart = get_or_create_cart(request)
    
    # KHÔNG BAO GIỜ giữ coupon khi vào lại trang - LUÔN reset
    # Xóa coupon và selected_items khỏi session mỗi khi vào trang giỏ hàng
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
    if 'selected_cart_items' in request.session:
        del request.session['selected_cart_items']
    
    # Khởi tạo mặc định
    applied_coupon = None
    coupon_discount_amount = 0
    selected_items = []
    
    context = {
        'cart': cart,
        'applied_coupon': applied_coupon,
        'coupon_discount_amount': coupon_discount_amount,
        'page_title': 'Giỏ hàng - PhoneShop',
    }
    
    return render(request, 'cart/detail.html', context)
    
    return render(request, 'cart/detail.html', context)


@require_POST
def cart_add(request, product_id):
    """
    Thêm sản phẩm vào giỏ hàng.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    # Lấy dữ liệu từ form
    storage = request.POST.get('storage', '')
    color = request.POST.get('color', '')
    quantity = int(request.POST.get('quantity', 1))
    
    # Xác định giá - ưu tiên storage price nếu có
    if storage:
        storage_obj = product.storage_options.filter(storage=storage).first()
        if storage_obj:
            price = storage_obj.sale_price
        else:
            price = product.sale_price
    else:
        price = product.sale_price
    
    # Kiểm tra sản phẩm đã có trong giỏ chưa (cùng product, storage, color)
    existing_item = cart.items.filter(
        product=product,
        storage=storage,
        color=color
    ).first()
    
    if existing_item:
        # Cập nhật số lượng
        existing_item.quantity += quantity
        existing_item.save()
        messages.success(request, f'Đã cập nhật số lượng {product.name}')
    else:
        # Tạo mới
        CartItem.objects.create(
            cart=cart,
            product=product,
            storage=storage,
            color=color,
            quantity=quantity,
            price=price
        )
        messages.success(request, f'Đã thêm {product.name} vào giỏ hàng')
    
    return redirect('cart_detail')


@require_POST
def cart_update(request, item_id):
    """
    Cập nhật số lượng sản phẩm trong giỏ hàng.
    """
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        item.quantity = quantity
        item.save()
        messages.success(request, 'Đã cập nhật giỏ hàng')
    else:
        item.delete()
        messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng')
    
    return redirect('cart_detail')


@require_POST
def cart_remove(request, item_id):
    """
    Xóa sản phẩm khỏi giỏ hàng (AJAX).
    """
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    product_name = item.product.name
    item.delete()
    
    # Tính lại tổng
    remaining_items = cart.items.all()
    new_subtotal = sum(i.subtotal for i in remaining_items)
    new_count = remaining_items.count()
    
    return JsonResponse({
        'success': True,
        'message': f'Đã xóa {product_name} khỏi giỏ hàng',
        'remaining_count': new_count,
        'subtotal': new_subtotal
    })


def cart_clear(request):
    """
    Xóa tất cả sản phẩm trong giỏ hàng (AJAX).
    """
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Đã xóa toàn bộ giỏ hàng',
        'remaining_count': 0,
        'subtotal': 0
    })


@require_POST
def cart_update_all(request):
    """
    Cập nhật số lượng cho tất cả sản phẩm trong giỏ.
    """
    cart = get_or_create_cart(request)
    
    for item in cart.items.all():
        quantity = int(request.POST.get(f'quantity_{item.id}', item.quantity))
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
    
    messages.success(request, 'Đã cập nhật giỏ hàng')
    return redirect('cart_detail')


@require_POST
def cart_remove_bulk(request):
    """
    Xóa nhiều sản phẩm đã chọn khỏi giỏ hàng.
    """
    cart = get_or_create_cart(request)
    selected_items = request.POST.getlist('selected_items')
    
    if selected_items:
        deleted_count = cart.items.filter(id__in=selected_items).delete()[0]
        messages.success(request, f'Đã xóa {deleted_count} sản phẩm đã chọn')
    else:
        messages.warning(request, 'Vui lòng chọn sản phẩm cần xóa')
    
    return redirect('cart_detail')


# =====================
# THANH TOÁN (CHECKOUT)
# =====================

def checkout_view(request):
    """
    Trang thanh toán.
    Hiển thị địa chỉ, sản phẩm đã chọn, voucher và nút đặt hàng.
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Vui lòng đăng nhập để thanh toán.')
        return redirect('login')
    
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, 'Giỏ hàng trống.')
        return redirect('home')
    
    # Lấy danh sách sản phẩm được chọn từ session
    selected_items = request.session.get('selected_cart_items', [])
    if not selected_items:
        # Nếu không có session, lấy tất cả
        selected_items = list(cart.items.values_list('id', flat=True))
    
    # Lọc các sản phẩm được chọn
    cart_items = cart.items.filter(id__in=selected_items)
    
    if not cart_items.exists():
        messages.warning(request, 'Vui lòng chọn sản phẩm để thanh toán.')
        return redirect('cart_detail')
    
    # Tính tổng tiền
    subtotal = sum(item.subtotal for item in cart_items)
    
    # Lấy địa chỉ mặc định
    default_address = request.user.shipping_addresses.filter(is_default=True).first()
    if not default_address:
        default_address = request.user.shipping_addresses.first()
    
    # Xử lý voucher từ session
    coupon_code = request.session.get('applied_coupon')
    coupon = None
    discount_amount = 0
    
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
        if coupon:
            product_count = cart_items.count()
            # Kiểm tra giới hạn sản phẩm
            if coupon.max_product_limit > 0 and product_count > coupon.max_product_limit:
                # Xóa coupon khỏi session
                del request.session['applied_coupon']
                coupon = None
                messages.warning(request, f'Voucher chỉ áp dụng cho tối đa {coupon.max_product_limit} sản phẩm. Vui lòng chọn lại sản phẩm.')
                return redirect('cart_detail')
            discount_amount = coupon.calculate_discount(subtotal)
    
    total = subtotal - discount_amount
    if total < 0:
        total = 0
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'coupon': coupon,
        'discount_amount': discount_amount,
        'total': total,
        'default_address': default_address,
        'page_title': 'Thanh toán - PhoneShop',
    }
    
    return render(request, 'cart/checkout.html', context)


@require_POST
def checkout_place_order(request):
    """
    Xử lý đặt hàng.
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Vui lòng đăng nhập.')
        return redirect('login')
    
    cart = get_or_create_cart(request)
    
    # Lấy danh sách sản phẩm được chọn
    selected_items = request.session.get('selected_cart_items', [])
    if not selected_items:
        selected_items = list(cart.items.values_list('id', flat=True))
    
    cart_items = cart.items.filter(id__in=selected_items)
    
    if not cart_items.exists():
        messages.warning(request, 'Không có sản phẩm để thanh toán.')
        return redirect('cart_detail')
    
    # Lấy thông tin từ form
    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    payment_method = request.POST.get('payment_method', 'cod')
    note = request.POST.get('note', '').strip()
    
    if not full_name or not phone or not address:
        messages.error(request, 'Vui lòng nhập đầy đủ thông tin giao hàng.')
        return redirect('checkout')
    
    # Tính tổng tiền
    subtotal = sum(item.subtotal for item in cart_items)
    
    # Xử lý voucher
    coupon_code = request.session.get('applied_coupon')
    coupon = None
    discount_amount = 0
    
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
        if coupon:
            # KIỂM TRA: Voucher có giới hạn email không?
            if coupon.usage_type == 'specific':
                user_email = request.user.email.lower()
                target_email = coupon.specific_email.lower() if coupon.specific_email else ''
                
                if user_email != target_email:
                    del request.session['applied_coupon']
                    messages.error(request, f'Xin lỗi tài khoản của bạn không thể dùng được Voucher này.')
                    return redirect('cart_detail')
            
            # KIỂM TRA: User đã dùng voucher này chưa?
            used_user_voucher = UserVoucher.objects.filter(
                user=request.user,
                coupon=coupon,
                is_used=True
            ).exists()
            used_in_order = Order.objects.filter(
                user=request.user,
                coupon_code=coupon.code
            ).exists()
            
            if used_user_voucher or used_in_order:
                del request.session['applied_coupon']
                messages.error(request, 'Bạn đã sử dụng voucher này rồi!')
                return redirect('cart_detail')
            
            product_count = cart_items.count()
            # Kiểm tra giới hạn sản phẩm
            if coupon.max_product_limit > 0 and product_count > coupon.max_product_limit:
                # Xóa coupon khỏi session và chuyển về giỏ hàng
                del request.session['applied_coupon']
                messages.warning(request, f'Voucher chỉ áp dụng cho tối đa {coupon.max_product_limit} sản phẩm. Vui lòng chọn lại sản phẩm.')
                return redirect('cart_detail')
            discount_amount = coupon.calculate_discount(subtotal)
    
    total = subtotal - discount_amount
    if total < 0:
        total = 0
    
    # Tạo đơn hàng
    order = Order.objects.create(
        user=request.user,
        full_name=full_name,
        phone=phone,
        address=address,
        payment_method=payment_method,
        payment_status='unpaid' if payment_method == 'online' else 'cod',
        subtotal=subtotal,
        discount_amount=discount_amount,
        coupon_code=coupon_code or '',
        total=total,
        note=note,
    )
    
    # Tạo các sản phẩm trong đơn hàng
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=f"{item.product.brand} {item.product.name}",
            storage=item.storage,
            color=item.color,
            quantity=item.quantity,
            price=item.price,
        )
    
    # Xóa sản phẩm đã đặt khỏi giỏ hàng
    cart_items.delete()
    
    # Xóa voucher khỏi session
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
    if 'selected_cart_items' in request.session:
        del request.session['selected_cart_items']
    
    # Cập nhật UserVoucher: đánh dấu đã sử dụng thay vì xóa
    if coupon:
        user_voucher = UserVoucher.objects.filter(user=request.user, coupon=coupon, is_used=False).first()
        if user_voucher:
            from django.utils import timezone
            user_voucher.is_used = True
            user_voucher.used_at = timezone.now()
            user_voucher.order = order
            user_voucher.save()
    
    # Lưu order_id vào session để hiển thị trang thành công
    request.session['last_order_id'] = order.id
    
    return redirect('checkout_success')


def checkout_success(request):
    """
    Trang thông báo đặt hàng thành công.
    """
    order_id = request.session.get('last_order_id')
    
    if not order_id:
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'page_title': 'Đặt hàng thành công - PhoneShop',
    }
    
    return render(request, 'cart/success.html', context)


@login_required
def order_tracking(request):
    """
    Trang tra cứu đơn hàng của người dùng.
    Hiển thị danh sách đơn hàng đã đặt với trạng thái.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'Tra cứu đơn hàng - PhoneShop',
    }
    
    return render(request, 'cart/order_tracking.html', context)


@login_required
def order_detail(request, order_id):
    """
    Trang chi tiết một đơn hàng.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'page_title': f'Đơn hàng #{order.id} - PhoneShop',
    }
    
    return render(request, 'cart/order_detail.html', context)


@require_POST
@login_required
def order_cancel(request, order_id):
    """
    Hủy đơn hàng (chỉ khi đơn hàng đang ở trạng thái 'pending').
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Chỉ cho phép hủy khi đơn hàng đang ở trạng thái 'pending' (Chờ duyệt)
    if order.status != 'pending':
        messages.error(request, 'Chỉ có thể hủy đơn hàng khi đang chờ duyệt.')
        return redirect('order_tracking')
    
    # Cập nhật trạng thái đơn hàng
    order.status = 'cancelled'
    order.save()
    
    messages.success(request, f'Đơn hàng #{order.id} đã được hủy thành công.')
    return redirect('order_tracking')


@require_POST
def apply_coupon(request):
    """
    Áp dụng mã giảm giá.
    Kiểm tra user đã dùng voucher này chưa.
    Kiểm tra voucher có giới hạn email không.
    """
    code = request.POST.get('code', '').strip().upper()
    
    if not code:
        return JsonResponse({'success': False, 'message': 'Vui lòng nhập mã giảm giá.'})
    
    coupon = Coupon.objects.filter(code=code, is_active=True).first()
    
    if not coupon:
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']
        return JsonResponse({'success': False, 'message': 'Mã giảm giá không hợp lệ hoặc đã hết hạn.'})
    
    # KIỂM TRA: User đã đăng nhập chưa?
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Vui lòng đăng nhập để sử dụng mã giảm giá.'
        })
    
    # KIỂM TRA: Voucher có giới hạn email không?
    if coupon.usage_type == 'specific':
        user_email = request.user.email.lower()
        target_email = coupon.specific_email.lower() if coupon.specific_email else ''
        
        if user_email != target_email:
            return JsonResponse({
                'success': False,
                'message': f'Xin lỗi tài khoản của bạn không thể dùng được Voucher này.'
            })
    
    # KIỂM TRA: User đã dùng voucher này chưa?
    # Cách 1: Kiểm tra từ UserVoucher (is_used=True)
    used_user_voucher = UserVoucher.objects.filter(
        user=request.user,
        coupon=coupon,
        is_used=True
    ).exists()
    
    # Cách 2: Kiểm tra từ Order history (nếu voucher cũ không có UserVoucher)
    used_in_order = Order.objects.filter(
        user=request.user,
        coupon_code=coupon.code
    ).exists()
    
    if used_user_voucher or used_in_order:
        return JsonResponse({
            'success': False,
            'message': 'Bạn đã sử dụng voucher này rồi!'
        })
    
    # Lấy sản phẩm được chọn từ POST hoặc session
    cart = get_or_create_cart(request)
    
    # Thử lấy từ POST trước
    selected_items_post = request.POST.get('selected_items', '')
    if selected_items_post:
        try:
            import json
            selected_items = json.loads(selected_items_post)
            # Lưu vào session để giữ trạng thái
            request.session['selected_cart_items'] = [int(id) for id in selected_items]
        except:
            selected_items = request.session.get('selected_cart_items', [])
    else:
        selected_items = request.session.get('selected_cart_items', [])
    
    # KIỂM TRA: Nếu chưa chọn sản phẩm nào, báo lỗi
    if not selected_items:
        return JsonResponse({
            'success': False, 
            'message': 'Vui lòng chọn sản phẩm trước khi áp dụng mã giảm giá.'
        })
    
    cart_items = cart.items.filter(id__in=selected_items)
    product_count = cart_items.count()
    
    # KIỂM TRA GIỚI HẠN SẢN PHẨM
    if coupon.max_product_limit > 0 and product_count > coupon.max_product_limit:
        return JsonResponse({
            'success': False, 
            'message': f'Voucher chỉ áp dụng cho tối đa {coupon.max_product_limit} sản phẩm. Bạn đang chọn {product_count} sản phẩm.'
        })
    
    # Lưu vào session
    request.session['applied_coupon'] = code
    
    # Tạo UserVoucher record cho user (nếu chưa có)
    if request.user.is_authenticated:
        existing_uv = None
        
        # Trường hợp 1: Voucher cho email cụ thể (usage_type='specific')
        if coupon.usage_type == 'specific':
            # Tìm UserVoucher gốc được tạo cho email cụ thể
            existing_uv = UserVoucher.objects.filter(
                coupon=coupon,
                is_used=False
            ).first()
            
            # Nếu tìm thấy UserVoucher gốc, cập nhật user cho record này
            if existing_uv:
                existing_uv.user = request.user
                existing_uv.save()
        
        # Trường hợp 2: Voucher cho mọi người (usage_type='all')
        if not existing_uv:
            # Kiểm tra xem user hiện tại đã có UserVoucher chưa
            existing_uv = UserVoucher.objects.filter(
                user=request.user, 
                coupon=coupon,
                is_used=False
            ).first()
        
        # Nếu không có record nào, tạo mới
        if not existing_uv:
            UserVoucher.objects.create(
                user=request.user,
                coupon=coupon
            )
    
    # Tính lại tổng tiền
    subtotal = sum(item.subtotal for item in cart_items)
    discount = coupon.calculate_discount(subtotal)
    total = subtotal - discount
    
    return JsonResponse({
        'success': True,
        'message': f'Áp dụng mã {code} thành công!',
        'coupon_code': code,
        'discount_value': coupon.discount_value,
        'discount_type': coupon.discount_type,
        'discount_amount': int(discount),
        'total': int(total),
    })


def remove_coupon(request):
    """
    Xóa mã giảm giá đã áp dụng.
    """
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
    
    messages.success(request, 'Đã hủy mã giảm giá.')
    return redirect('cart_detail')


def buy_now(request, product_id):
    """
    Mua ngay - Thêm sản phẩm vào giỏ và chuyển đến giỏ hàng.
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Vui lòng đăng nhập để mua hàng.')
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    # Lấy thông tin từ form
    storage = request.POST.get('storage', '')
    color = request.POST.get('color', '')
    quantity = int(request.POST.get('quantity', 1))
    
    # Xác định giá
    if storage:
        storage_obj = product.storage_options.filter(storage=storage).first()
        if storage_obj:
            price = storage_obj.sale_price
        else:
            price = product.sale_price
    else:
        price = product.sale_price
    
    # Thêm vào giỏ hàng
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        storage=storage,
        color=color,
        defaults={'price': price, 'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    # Lưu sản phẩm được chọn vào session
    request.session['selected_cart_items'] = [cart_item.id]
    
    messages.success(request, f'Đã thêm {product.name} vào giỏ hàng.')
    return redirect('cart_detail')


@require_POST
def select_cart_items(request):
    """
    Lưu danh sách sản phẩm được chọn vào session.
    """
    import json
    
    # Lấy dữ liệu từ AJAX request
    raw_data = request.POST.get('selected_items', '[]')
    
    try:
        selected_ids = json.loads(raw_data)
    except (json.JSONDecodeError, TypeError, ValueError):
        selected_ids = []
    
    # Lưu vào session
    request.session['selected_cart_items'] = [int(id) for id in selected_ids] if selected_ids else []
    
    # Nếu là AJAX request, trả về JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    # Nếu là form submission thông thường
    if not selected_ids:
        messages.warning(request, 'Vui lòng chọn sản phẩm để thanh toán.')
        return redirect('cart_detail')
    
    return redirect('checkout')


@login_required
def feedback_create(request):
    """
    Tạo mới góp ý.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if not title or not content:
            messages.error(request, 'Vui lòng nhập đầy đủ tiêu đề và nội dung.')
        else:
            Feedback.objects.create(
                user=request.user,
                title=title,
                content=content
            )
            messages.success(request, 'Góp ý của bạn đã được gửi! Chúng tôi sẽ phản hồi sớm nhất.')
        
        return redirect('profile')
    
    return redirect('profile')


@login_required
def feedback_list(request):
    """
    Lấy danh sách góp ý của user (AJAX).
    """
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    data = [{
        'id': f.id,
        'title': f.title,
        'content': f.content,
        'admin_response': f.admin_response,
        'created_at': f.created_at.strftime('%d/%m/%Y %H:%M'),
        'responded_at': f.responded_at.strftime('%d/%m/%Y %H:%M') if f.responded_at else None,
        'is_responded': f.is_responded
    } for f in feedbacks]
    
    return JsonResponse({'feedbacks': data})


# ==================== ADMIN MANAGEMENT VIEWS ====================

@user_passes_test(is_admin)
def admin_orders(request):
    """
    Trang quản lý đơn hàng (admin).
    """
    orders = Order.objects.all().prefetch_related('items').order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'Quản lý đơn hàng - Admin',
    }
    
    return render(request, 'admin/orders.html', context)


@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    """
    Trang chi tiết đơn hàng (admin).
    """
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            # Tự động cập nhật trạng thái thanh toán khi đơn hàng hoàn thành
            if new_status == 'completed':
                # Nếu là thanh toán COD, tự động đánh dấu đã thanh toán
                if order.payment_method == 'cod':
                    order.payment_status = 'paid'
                # Nếu là thanh toán online, giữ nguyên
            order.save()
            messages.success(request, 'Cập nhật trạng thái đơn hàng thành công!')
            return redirect('admin_order_detail', order_id=order_id)
    
    context = {
        'order': order,
        'order_items': order_items,
        'page_title': f'Đơn hàng #{order.id} - Admin',
    }
    
    return render(request, 'admin/order_detail.html', context)


@user_passes_test(is_admin)
def admin_vouchers(request):
    """
    Trang quản lý voucher (admin).
    Hiển thị số lần voucher đã được sử dụng và danh sách đơn hàng.
    """
    vouchers = Coupon.objects.all().order_by('-id')
    
    # Đếm số lần sử dụng và lấy danh sách đơn hàng cho mỗi voucher
    voucher_data = {}
    
    for voucher in vouchers:
        orders = Order.objects.filter(
            coupon_code=voucher.code
        ).exclude(
            coupon_code__isnull=True
        ).exclude(
            coupon_code=''
        ).select_related('user').order_by('-created_at')[:10]  # 10 đơn hàng gần nhất
        
        voucher_data[voucher.id] = {
            'count': orders.count(),
            'orders': list(orders)
        }
    
    context = {
        'vouchers': vouchers,
        'voucher_data': voucher_data,
        'page_title': 'Quản lý voucher - Admin',
    }
    
    return render(request, 'admin/vouchers.html', context)


@user_passes_test(is_admin)
def admin_voucher_add(request):
    """
    Trang thêm voucher mới (admin).
    """
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        description = request.POST.get('description', '').strip()
        discount_type = request.POST.get('discount_type')
        discount_value = int(request.POST.get('discount_value', '0') or 0)
        min_order = int(request.POST.get('min_order', '0') or 0)
        max_usage_per_user = int(request.POST.get('max_usage_per_user', '1') or 1)
        max_product_limit = int(request.POST.get('max_product_limit', '0') or 0)
        usage_type = request.POST.get('usage_type', 'all')
        specific_email = request.POST.get('specific_email', '').strip() if usage_type == 'specific' else None
        is_indefinite = request.POST.get('is_indefinite') == 'on'
        expires_at = request.POST.get('expires_at')
        is_active = request.POST.get('is_active') == 'on'
        
        if code and discount_value:
            coupon = Coupon.objects.create(
                code=code,
                description=description,
                discount_type=discount_type,
                discount_value=discount_value,
                min_order=min_order,
                max_usage_per_user=max_usage_per_user,
                max_product_limit=max_product_limit,
                usage_type=usage_type,
                specific_email=specific_email,
                expires_at=None if is_indefinite else (expires_at if expires_at else None),
                is_active=is_active
            )
            
            # Nếu là voucher cho email cụ thể, tự động gán cho user đó
            if usage_type == 'specific' and specific_email:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    target_user = User.objects.get(email=specific_email)
                    
                    # Kiểm tra xem user đã có voucher này chưa
                    existing = UserVoucher.objects.filter(user=target_user, coupon=coupon).exists()
                    if not existing:
                        UserVoucher.objects.create(user=target_user, coupon=coupon)
                        messages.success(request, f'Tạo voucher thành công! Đã gán cho {specific_email}')
                    else:
                        messages.success(request, f'Tạo voucher thành công! User đã có voucher này')
                except User.DoesNotExist:
                    messages.warning(request, f'Tạo voucher thành công! Nhưng user {specific_email} không tồn tại')
                except Exception as e:
                    messages.warning(request, f'Tạo voucher thành công! Lỗi gán cho user: {str(e)}')
            else:
                messages.success(request, 'Tạo voucher thành công!')
            
            return redirect('admin_vouchers')
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin!')
    
    context = {
        'page_title': 'Thêm voucher mới - Admin',
    }
    
    return render(request, 'admin/voucher_form.html', context)


@user_passes_test(is_admin)
def admin_voucher_edit(request, voucher_id):
    """
    Trang chỉnh sửa voucher (admin).
    """
    voucher = get_object_or_404(Coupon, id=voucher_id)
    
    if request.method == 'POST':
        voucher.code = request.POST.get('code', '').strip().upper()
        voucher.description = request.POST.get('description', '').strip()
        voucher.discount_type = request.POST.get('discount_type')
        voucher.discount_value = int(request.POST.get('discount_value', '0') or 0)
        voucher.min_order = int(request.POST.get('min_order', '0') or 0)
        voucher.max_usage_per_user = int(request.POST.get('max_usage_per_user', '1') or 1)
        voucher.max_product_limit = int(request.POST.get('max_product_limit', '0') or 0)
        voucher.usage_type = request.POST.get('usage_type', 'all')
        voucher.specific_email = request.POST.get('specific_email', '').strip() if request.POST.get('usage_type') == 'specific' else None
        is_indefinite = request.POST.get('is_indefinite') == 'on'
        expires_at = request.POST.get('expires_at')
        voucher.expires_at = None if is_indefinite else (expires_at if expires_at else None)
        voucher.is_active = request.POST.get('is_active') == 'on'
        voucher.save()
        messages.success(request, 'Cập nhật voucher thành công!')
        return redirect('admin_vouchers')
    
    context = {
        'voucher': voucher,
        'page_title': 'Chỉnh sửa voucher - Admin',
    }
    
    return render(request, 'admin/voucher_form.html', context)


@user_passes_test(is_admin)
def admin_voucher_delete(request, voucher_id):
    """
    Xóa voucher (admin).
    """
    voucher = get_object_or_404(Coupon, id=voucher_id)
    voucher.delete()
    messages.success(request, 'Xóa voucher thành công!')
    return redirect('admin_vouchers')


@user_passes_test(is_admin)
def admin_feedbacks(request):
    """
    Trang quản lý góp ý (admin).
    """
    from django.utils import timezone
    feedbacks = Feedback.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        admin_response = request.POST.get('admin_response', '').strip()
        
        if feedback_id and admin_response:
            feedback = get_object_or_404(Feedback, id=feedback_id)
            feedback.admin_response = admin_response
            feedback.responded_at = timezone.now()
            feedback.save()
            messages.success(request, 'Phản hồi góp ý thành công!')
        
        return redirect('admin_feedbacks')
    
    context = {
        'feedbacks': feedbacks,
        'page_title': 'Quản lý góp ý - Admin',
    }
    
    return render(request, 'admin/feedbacks.html', context)


@user_passes_test(is_admin)
def admin_users(request):
    """
    Trang quản lý người dùng (admin) - có phân trang và tìm kiếm.
    """
    from django.core.paginator import Paginator
    
    query = request.GET.get('q', '').strip()
    
    users = User.objects.all().order_by('-date_joined')
    
    # Tìm kiếm theo username, email, số điện thoại
    if query:
        users = users.filter(
            models.Q(username__icontains=query) |
            models.Q(email__icontains=query) |
            models.Q(profile__phone_number__icontains=query)
        )
    
    # Phân trang - 5 người dùng mỗi trang
    paginator = Paginator(users, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'page_title': 'Quản lý người dùng - Admin',
        'query': query,
    }
    
    return render(request, 'admin/users.html', context)


@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """
    Trang chi tiết người dùng (admin) - xem và chỉnh sửa thông tin.
    """
    user = get_object_or_404(User, id=user_id)
    
    # Lấy thông tin profile
    try:
        profile = user.profile
    except:
        profile = None
    
    # Lấy địa chỉ mặc định
    default_address = user.shipping_addresses.filter(is_default=True).first()
    addresses = user.shipping_addresses.all()
    
    # Lấy đơn hàng gần đây (sử dụng related_name='orders')
    orders = user.orders.all().order_by('-created_at')[:10]
    
    # Lấy voucher (sử dụng related_name='user_vouchers') - CHỈ lấy voucher CHƯA sử dụng
    user_vouchers = user.user_vouchers.filter(is_used=False).select_related('coupon')
    
    if request.method == 'POST':
        # Cập nhật thông tin user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        
        # Cập nhật phone nếu có profile
        if profile:
            phone = request.POST.get('phone', '').strip()
            profile.phone_number = phone
            profile.save()
        
        messages.success(request, 'Cập nhật thông tin người dùng thành công!')
        return redirect('admin_user_detail', user_id=user_id)
    
    context = {
        'user': user,
        'profile': profile,
        'default_address': default_address,
        'addresses': addresses,
        'orders': orders,
        'user_vouchers': user_vouchers,
        'page_title': f'Người dùng: {user.username} - Admin',
    }
    
    return render(request, 'admin/user_detail.html', context)


@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    """
    Xóa người dùng (admin).
    """
    user = get_object_or_404(User, id=user_id)
    
    # Không cho phép xóa admin
    if user.is_superuser:
        messages.error(request, 'Không thể xóa tài khoản admin!')
    else:
        user.delete()
        messages.success(request, 'Xóa người dùng thành công!')
    
    return redirect('admin_users')


@user_passes_test(is_admin)
def admin_reviews(request):
    """
    Trang quản lý đánh giá (admin).
    Hiển thị danh sách đánh giá với thông tin người dùng và sản phẩm.
    Chỉ cho phép xóa đánh giá.
    """
    from django.core.paginator import Paginator
    
    reviews = Review.objects.all().select_related('user', 'product').order_by('-created_at')
    
    # Phân trang - 10 đánh giá mỗi trang
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reviews': page_obj,
        'page_title': 'Quản lý đánh giá - Admin',
    }
    
    return render(request, 'admin/reviews.html', context)


@user_passes_test(is_admin)
@require_POST
def admin_review_delete(request, review_id):
    """
    Xóa đánh giá (admin).
    """
    review = get_object_or_404(Review, id=review_id)
    product_name = review.product.name if review.product else 'Sản phẩm đã xóa'
    user_username = review.user.username
    
    review.delete()
    messages.success(request, f'Đã xóa đánh giá của {user_username} cho sản phẩm {product_name}')
    
    return redirect('admin_reviews')

