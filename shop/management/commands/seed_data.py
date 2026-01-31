"""
Management command de tao du lieu mau.
Su dung: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Product, ProductImage, StorageOption, ColorOption, Coupon, Review
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from io import BytesIO
from PIL import Image


class Command(BaseCommand):
    help = 'Tao du lieu mau cho cua hang dien thoai'

    def handle(self, *args, **options):
        self.stdout.write('[INFO] Bat dau tao du lieu mau...\n')
        
        # Tao admin user
        self.create_admin_user()
        
        # Tao coupon
        self.create_coupons()
        
        # Tao san pham mau
        self.create_sample_products()
        
        self.stdout.write(self.style.SUCCESS('\n[OK] Da tao du lieu mau thanh cong!'))

    def create_admin_user(self):
        """Tao tai khoan admin mac dinh."""
        if not User.objects.filter(username='qhun22').exists():
            User.objects.create_user(
                username='qhun22',
                password='1',
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write('  [OK] Da tao tai khoan admin: qhun22 / 1')
        else:
            self.stdout.write('  [INFO] Tai khoan admin qhun22 da ton tai')

    def create_coupons(self):
        """Tao cac ma giam gia mau."""
        coupons = [
            {'code': 'WELCOME10', 'percent': 10},
            {'code': 'SALE20', 'percent': 20},
            {'code': 'VIP30', 'percent': 30},
        ]
        
        for coupon_data in coupons:
            if not Coupon.objects.filter(code=coupon_data['code']).exists():
                Coupon.objects.create(
                    code=coupon_data['code'],
                    percent_discount=coupon_data['percent'],
                    is_active=True
                )
                self.stdout.write(f"  [OK] Da tao ma giam gia: {coupon_data['code']} ({coupon_data['percent']}%)")
            else:
                self.stdout.write(f"  [INFO] Ma {coupon_data['code']} da ton tai")

    def create_sample_products(self):
        """Tao cac san pham mau voi anh placeholder."""
        
        # Tao anh placeholder don gian
        def create_placeholder_image(color=(100, 100, 255), text='Phone'):
            """Tao anh placeholder don gian."""
            img = Image.new('RGB', (400, 400), color)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return SimpleUploadedFile(
                f'{text}.png',
                buffer.read(),
                content_type='image/png'
            )
        
        # Danh sach san pham mau
        sample_products = [
            {
                'brand': 'Apple',
                'name': 'iPhone 15 Pro Max',
                'description': '''iPhone 15 Pro Max la phien ban cao cap nhat cua iPhone 15 voi nhieu cai tien vuot troi.

Diem noi bat:
- Chip A17 Pro manh me, tiet kiem nang luong
- Khung titan nhe va ben
- Camera 48MP voi kha nang zoom quang hoc 5x
- Cong USB-C tien loi
- Dynamic Island thong minh''',
                'specifications': '''- Man hinh: 6.7 inch Super Retina XDR OLED, 2796 x 1290 pixels
- Chip: A17 Pro 6 nhan
- RAM: 8GB
- Bo nho trong: 256GB/512GB/1TB
- Camera chinh: 48MP, f/1.8, OIS
- Camera telephoto: 12MP, f/2.8, 5x optical zoom
- Camera ultrawide: 12MP, f/2.2
- Camera truoc: 12MP, f/1.9
- Pin: 4422 mAh
- Sac: USB-C, MagSafe 15W
- Kich thuoc: 159.9 x 76.7 x 8.25 mm
- Trong luong: 221g''',
                'original_price': 34990000,
                'sale_price': 29990000,
                'discount_percent': 14,  # Tu dong tinh: (34990000-29990000)/34990000*100 = 14%
                'warranty_months': 24,
                'free_shipping': True,
                'open_box_check': True,
                'return_30_days': True,
                'youtube_id': 'Zk1sCvp0WwY',
                'storages': [
                    ('256GB', 34990000),
                    ('512GB', 38990000),
                    ('1TB', 42990000),
                ],
                'colors': [
                    ('Natural Titanium', (194, 178, 128)),
                    ('Blue Titanium', (70, 100, 150)),
                    ('White Titanium', (240, 240, 240)),
                    ('Black Titanium', (30, 30, 30)),
                ],
            },
            {
                'brand': 'Samsung',
                'name': 'Galaxy S24 Ultra',
                'description': '''Samsung Galaxy S24 Ultra la flagship cao cap nhat cua Samsung voi S Pen tich hop va AI tien tien.

Diem noi bat:
- Chip Snapdragon 8 Gen 3 for Galaxy
- Camera 200MP sieu net
- S Pen tich hop
- AI Galaxy AI
- Man hinh Dynamic AMOLED 2X''',
                'specifications': '''- Man hinh: 6.8 inch QHD+ Dynamic AMOLED 2X, 3120 x 1440 pixels
- Chip: Snapdragon 8 Gen 3 for Galaxy
- RAM: 12GB
- Bo nho trong: 256GB/512GB/1TB
- Camera chinh: 200MP, f/1.7, OIS
- Camera telephoto: 50MP, f/3.4, 5x optical zoom
- Camera telephoto 2: 10MP, f/2.4, 3x optical zoom
- Camera ultrawide: 12MP, f/2.2
- Camera truoc: 12MP, f/2.2
- Pin: 5000 mAh
- Sac: USB-C, 45W wired, 15W wireless
- Kich thuoc: 162.3 x 79.0 x 8.6 mm
- Trong luong: 232g
- S Pen: Co''',
                'original_price': 32990000,
                'sale_price': 27990000,
                'warranty_months': 24,
                'free_shipping': True,
                'open_box_check': True,
                'return_30_days': True,
                'youtube_id': 'Rj_7eFw7wKg',
                'storages': [
                    ('256GB', 32990000),
                    ('512GB', 36990000),
                    ('1TB', 40990000),
                ],
                'colors': [
                    ('Titanium Black', (20, 20, 20)),
                    ('Titanium Gray', (100, 100, 100)),
                    ('Titanium Violet', (120, 80, 150)),
                    ('Titanium Yellow', (220, 200, 50)),
                ],
            },
        ]
        
        # Tao thu muc media neu chua co
        from django.conf import settings
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'products'), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'products', 'gallery'), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'products', 'colors'), exist_ok=True)
        
        # Tao san pham
        for product_data in sample_products:
            # Kiem tra san pham da ton tai chua
            if Product.objects.filter(name=product_data['name']).exists():
                self.stdout.write(f"  [INFO] {product_data['brand']} {product_data['name']} da ton tai")
                continue
            
            # Tao anh chinh
            main_image = create_placeholder_image(
                color=product_data['colors'][0][1] if product_data['colors'] else (100, 100, 255),
                text=f"{product_data['brand']}_{product_data['name']}".replace(' ', '_')
            )
            
            # Tao san pham
            product = Product.objects.create(
                brand=product_data['brand'],
                name=product_data['name'],
                main_image=main_image,
                description=product_data['description'],
                specifications=product_data['specifications'],
                original_price=product_data['original_price'],
                sale_price=product_data['sale_price'],
                discount_percent=product_data.get('discount_percent', 0),
                warranty_months=product_data['warranty_months'],
                free_shipping=product_data['free_shipping'],
                open_box_check=product_data['open_box_check'],
                return_30_days=product_data['return_30_days'],
                youtube_id=product_data.get('youtube_id', ''),
            )
            
            # Tao anh gallery
            for i in range(3):
                gallery_image = create_placeholder_image(
                    color=(150 + i*30, 150 + i*20, 200 + i*15),
                    text=f"{product.name}_gallery_{i+1}".replace(' ', '_')
                )
                ProductImage.objects.create(product=product, image=gallery_image)
            
            # Tao tuy chon bo nho
            for storage, price in product_data['storages']:
                StorageOption.objects.create(
                    product=product,
                    storage=storage,
                    original_price=price,
                )
            
            # Tao tuy chon mau sac
            for color_name, color_rgb in product_data['colors']:
                color_image = create_placeholder_image(
                    color=color_rgb,
                    text=f"{product.name}_{color_name}".replace(' ', '_')
                )
                ColorOption.objects.create(
                    product=product,
                    color_name=color_name,
                    color_image=color_image,
                )
            
            self.stdout.write(f"  [OK] Da tao san pham: {product.brand} {product.name}")
