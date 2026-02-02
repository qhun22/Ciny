# Generated migration for SpecialPromotion models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_remove_review_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialPromotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Hiển thị khuyến mãi')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
            ],
            options={
                'verbose_name': 'Khuyến mãi đặc biệt',
                'verbose_name_plural': 'Khuyến mãi đặc biệt',
            },
        ),
        migrations.CreateModel(
            name='SpecialPromotionProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_percent', models.PositiveIntegerField(default=0, verbose_name='Phần trăm giảm giá')),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='Thứ tự hiển thị')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày thêm')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product', verbose_name='Sản phẩm')),
                ('promotion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.specialpromotion', verbose_name='Khuyến mãi')),
            ],
            options={
                'verbose_name': 'Sản phẩm khuyến mãi',
                'verbose_name_plural': 'Sản phẩm khuyến mãi',
                'ordering': ['display_order'],
            },
        ),
        migrations.AddField(
            model_name='specialpromotion',
            name='products',
            field=models.ManyToManyField(related_name='special_promotions', through='shop.SpecialPromotionProduct', to='shop.product', verbose_name='Sản phẩm khuyến mãi'),
        ),
    ]
