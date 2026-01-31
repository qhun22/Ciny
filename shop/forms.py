"""
Forms for the phone shop application.
Các form cho ứng dụng bán điện thoại.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, Coupon, UserProfile


class RegistrationForm(UserCreationForm):
    """
    Form đăng ký người dùng mới.
    Sử dụng email làm tên đăng nhập.
    """
    full_name = forms.CharField(
        label="Họ và tên",
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nhập họ và tên của bạn',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Nhập email của bạn',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    phone_number = forms.CharField(
        label="Số điện thoại",
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nhập số điện thoại (10 số)',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nhập mật khẩu (ít nhất 6 ký tự)',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        help_text="Mật khẩu phải có ít nhất 6 ký tự."
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nhập lại mật khẩu',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        help_text="Nhập lại mật khẩu để xác nhận."
    )

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'password1', 'password2']

    def clean_email(self):
        """Kiểm tra email đã tồn tại chưa."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được đăng ký.")
        return email

    def clean_phone_number(self):
        """Kiểm tra số điện thoại đã tồn tại chưa."""
        phone = self.cleaned_data.get('phone_number')
        # Check if any user has this phone in their username (for backwards compatibility)
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError("Số điện thoại này đã được đăng ký.")
        return phone

    def save(self, commit=True):
        """
        Lưu user mới.
        Sử dụng email làm username để đăng nhập.
        """
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['full_name']
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
            # Save phone number to UserProfile
            phone = self.cleaned_data['phone_number']
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'phone_number': phone}
            )
        
        return user


class ReviewForm(forms.ModelForm):
    """
    Form để người dùng đánh giá sản phẩm.
    """
    
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        label="Đánh giá",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comment = forms.CharField(
        label="Bình luận",
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-textarea',
            'placeholder': 'Chia sẻ trải nghiệm của bạn...'
        })
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Đánh giá',
            'comment': 'Bình luận',
        }


class CouponForm(forms.Form):
    """
    Form nhập mã giảm giá trong trang chi tiết sản phẩm.
    """
    
    code = forms.CharField(
        label="Mã giảm giá",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nhập mã giảm giá'
        })
    )
    
    def clean_code(self):
        """Kiểm tra mã giảm giá có tồn tại và còn hiệu lực không."""
        code = self.cleaned_data['code'].upper()
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            return code
        except Coupon.DoesNotExist:
            raise forms.ValidationError("Mã giảm giá không tồn tại hoặc đã hết hạn.")


