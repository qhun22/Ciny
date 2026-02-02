"""
Telegram notification utility for order alerts.
"""
import requests
import json

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "8206672207:AAHY15AuxBDS9oMVsz8AVrodzGPx6_59Ul8"
TELEGRAM_CHAT_ID = "5032505212"


def send_telegram_message(message, parse_mode='HTML'):
    """
    Gửi thông báo đến Telegram.
    
    Args:
        message: Nội dung tin nhắn (hỗ trợ HTML format)
        parse_mode: 'HTML' hoặc 'Markdown'
    
    Returns:
        True nếu gửi thành công, False nếu thất bại
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False


def send_order_notification(order):
    """
    Gửi thông báo khi có đơn hàng mới.
    
    Args:
        order: Đối tượng Order
    """
    # Format số tiền
    from django.template.defaultfilters import floatformat
    total = f"{order.total:,.0f}".replace(',', '.')
    
    # Tạo nội dung tin nhắn
    message = f"""🛒 <b>ĐƠN HÀNG MỚI</b> #{order.id}

👤 <b>Khách hàng:</b> {order.full_name}
📞 <b>Điện thoại:</b> {order.phone}
📍 <b>Địa chỉ:</b> {order.address}

📦 <b>Sản phẩm:</b>
"""
    
    # Thêm danh sách sản phẩm
    for item in order.items.all():
        product_name = item.product_name
        message += f"• {product_name} x{item.quantity} - {item.price:,.0f}đ\n"
    
    message += f"""
 <b>Tổng tiền:</b> {total}đ
 <b>Thanh toán:</b> {'COD' if order.payment_method == 'cod' else 'Chuyển khoản'}
 <b>Ngày đặt:</b> {order.created_at.strftime('%d/%m/%Y %H:%M')}
"""
    
    return send_telegram_message(message)


