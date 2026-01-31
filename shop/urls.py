"""
URL configuration for the shop app.
Cấu hình URL cho ứng dụng shop.

Các trang:
- / : Trang chủ (danh sách sản phẩm)
- /product/<id>/ : Trang chi tiết sản phẩm
- /login/ : Trang đăng nhập
- /register/ : Trang đăng ký
- /logout/ : Xử lý đăng xuất
- /profile/ : Trang profile người dùng
- /qhun22/ : Trang quản trị admin (chỉ admin)
- /manage/products/ : Danh sách sản phẩm (quản lý)
- /manage/add-product/ : Trang thêm sản phẩm (chỉ admin)
- /manage/edit/<id>/ : Trang chỉnh sửa sản phẩm (chỉ admin)
- /manage/delete/<id>/ : Xóa sản phẩm (chỉ admin)
- /product/<id>/review/ : Xử lý thêm đánh giá
- /product/<id>/coupon/ : Xử lý áp dụng mã giảm giá
"""

from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ
    path('', views.home, name='home'),

    # Tìm kiếm sản phẩm
    path('products/search/', views.product_search, name='product_search'),

    # Trang chi tiết sản phẩm
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Xử lý thêm đánh giá
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    
    # Xử lý áp dụng mã giảm giá
    path('product/<int:product_id>/coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Trang đăng nhập, đăng ký, đăng xuất, quên mật khẩu
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    
    # Trang profile người dùng
    path('profile/', views.profile_view, name='profile'),
    
    # Trang quản trị admin
    path('qhun22/', views.admin_dashboard, name='admin_dashboard'),
    
    # Trang thêm sản phẩm (chỉ admin) - dùng manage/ thay vì admin/ để tránh xung đột
    path('manage/add-product/', views.admin_add_product, name='admin_add_product'),
    
    # Trang danh sách sản phẩm (quản lý)
    path('manage/products/', views.admin_product_list, name='admin_product_list'),
    
    # Trang chỉnh sửa sản phẩm (chỉ admin)
    path('manage/edit/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    
    # Xóa sản phẩm (chỉ admin)
    path('manage/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    
    # Giỏ hàng
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/update-all/', views.cart_update_all, name='cart_update_all'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/remove/bulk/', views.cart_remove_bulk, name='cart_remove_bulk'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    
    # Địa chỉ giao hàng
    path('profile/address/add/', views.address_add, name='address_add'),
    path('profile/address/default/<int:address_id>/', views.address_set_default, name='address_set_default'),
    path('profile/address/delete/<int:address_id>/', views.address_delete, name='address_delete'),
    
    # Voucher của user
    path('profile/voucher/delete/', views.voucher_delete, name='voucher_delete'),
    
    # Voucher
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('cart/remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('cart/select-items/', views.select_cart_items, name='select_cart_items'),
    
    # Mua ngay
    path('product/<int:product_id>/buy-now/', views.buy_now, name='buy_now'),
    
    # Thanh toán
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/place-order/', views.checkout_place_order, name='checkout_place_order'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    
    # Tra cứu đơn hàng
    path('orders/', views.order_tracking, name='order_tracking'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]

