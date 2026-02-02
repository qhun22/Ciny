"""
Test script for Telegram notification.
"""
import os
import sys
sys.path.insert(0, r'D:\Py\Ciny')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from core.telegram_utils import send_telegram_message

# Test message
test_message = """🛒 <b>TEST ĐƠN HÀNG MỚI</b> #999

👤 <b>Khách hàng:</b> Test User
📞 <b>Điện thoại:</b> 0123456789
📍 <b>Địa chỉ:</b> Test Address

📦 <b>Sản phẩm:</b>
• iPhone 15 x1 - 22.000.000đ

💰 <b>Tổng tiền:</b> 22.000.000đ
💳 <b>Thanh toán:</b> COD
📅 <b>Ngày đặt:</b> 02/02/2026 12:55
"""

print("Testing Telegram notification...")
if send_telegram_message(test_message):
    print("✅ Test message sent successfully!")
else:
    print("❌ Failed to send test message")

