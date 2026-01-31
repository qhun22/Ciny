"""
Context processor để thêm giỏ hàng vào tất cả các template.
"""

def cart_context(request):
    """
    Thêm thông tin giỏ hàng vào context của mọi template.
    """
    from shop.models import Cart
    
    cart = None
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
    
    return {
        'cart': cart,
    }

