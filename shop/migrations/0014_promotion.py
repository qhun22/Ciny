from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_add_special_promotion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False, verbose_name='Bật/Tắt hiển thị')),
                ('banner_image', models.ImageField(default='banners/bnv.png', upload_to='banners/', verbose_name='Ảnh banner')),
                ('max_products', models.PositiveIntegerField(default=5, verbose_name='Số sản phẩm tối đa hiển thị')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
            ],
            options={
                'verbose_name': 'Cấu hình khuyến mãi',
                'verbose_name_plural': 'Cấu hình khuyến mãi',
            },
        ),
        migrations.CreateModel(
            name='PromotionProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_percent', models.PositiveIntegerField(default=0, verbose_name='Phần trăm giảm giá (%)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày thêm')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promotion_items', to='shop.product', verbose_name='Sản phẩm')),
                ('promotion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promotion_products', to='shop.promotion', verbose_name='Khuyến mãi')),
            ],
            options={
                'verbose_name': 'Sản phẩm khuyến mãi',
                'verbose_name_plural': 'Sản phẩm khuyến mãi',
                'ordering': ['created_at'],
            },
        ),
    ]

