from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'
    
    def ready(self):
        """
        Hàm được gọi khi ứng dụng đã sẵn sàng.
        Đăng ký signals để tạo admin user và seed data sau khi migrate.
        """
        # Đăng ký signal post_migrate
        post_migrate.connect(create_admin_user_and_seed_data, sender=self)


def create_admin_user_and_seed_data(sender, **kwargs):
    """
    Tạo tài khoản admin mặc định và dữ liệu mẫu sau khi migrate.
    - Tài khoản admin: username=qhun22, password=1
    """
    from django.db import transaction
    from django.contrib.auth.models import User
    from .models import Coupon
    
    # Tạo admin user nếu chưa tồn tại
    if not User.objects.filter(username='qhun22').exists():
        try:
            user = User.objects.create_user(
                username='qhun22',
                password='1',
                is_staff=True,
                is_superuser=True,
            )
            print("[OK] Da tao tai khoan admin: qhun22 / 1")
        except Exception as e:
            print(f"[ERROR] Loi khi tao admin: {e}")
    else:
        print("[INFO] Tai khoan admin qhun22 da ton tai")
    
    # Tao coupon mau
    if not Coupon.objects.filter(code='WELCOME10').exists():
        try:
            Coupon.objects.create(
                code='WELCOME10',
                percent_discount=10,
                is_active=True
            )
            print("[OK] Da tao ma giam gia: WELCOME10 (10%)")
        except Exception as e:
            print(f"[ERROR] Loi khi tao coupon: {e}")
