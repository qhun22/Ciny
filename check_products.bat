@echo off
echo ============================================
echo Kiem tra san pham trong database
echo ============================================
cd /d %~dp0
echo.
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); import django; django.setup(); from shop.models import Product; products = Product.objects.all().order_by('id'); print(f'Tong so san pham: {products.count()}'); print(); [print(f'ID {p.id}: {p.brand} {p.name} | youtube_id: {p.youtube_id if p.youtube_id else \"(trong)\"}') for p in products]"
echo.
pause

