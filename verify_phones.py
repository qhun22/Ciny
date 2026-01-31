import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from shop.models import UserProfile

print("=== Setting is_phone_verified=True for users with phone ===")
profiles = UserProfile.objects.filter(phone_number__isnull=False)
for p in profiles:
    if not p.is_phone_verified:
        p.is_phone_verified = True
        p.save()
        print(f"Updated: {p.user.email} -> verified")

print(f"\nTotal verified: {UserProfile.objects.filter(is_phone_verified=True).count()}")
print("Done!")

