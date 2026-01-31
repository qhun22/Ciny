import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from shop.models import UserProfile

print("=== All User Profiles ===")
profiles = UserProfile.objects.all()
for p in profiles:
    email = p.user.email
    phone = p.phone_number or "(empty)"
    print(f"Email: {email}, Phone: {phone}")
