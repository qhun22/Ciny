import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

# Create UserVoucher table
cursor = connection.cursor()
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shop_uservoucher (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES auth_user(id),
            coupon_id INTEGER NOT NULL REFERENCES shop_coupon(id),
            created_at DATETIME NOT NULL
        )
    """)
    print("SUCCESS: Created shop_uservoucher table!")
except Exception as e:
    print(f"ERROR: {e}")

# Also add is_phone_verified column if not exists
try:
    cursor.execute("ALTER TABLE shop_userprofile ADD COLUMN is_phone_verified BOOLEAN DEFAULT 0")
    print("SUCCESS: Added is_phone_verified column!")
except:
    print("is_phone_verified column already exists or error")

