import sqlite3
import sys

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Connect to the database directly
db_path = r'D:\Py\Ciny\db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if QHUN22 coupon exists
cursor.execute("SELECT id, code FROM shop_coupon WHERE code = 'QHUN22'")
existing = cursor.fetchone()

if existing:
    print(f"[OK] Coupon QHUN22 already exists (ID: {existing[0]})")
else:
    # Create QHUN22 coupon
    cursor.execute("""
        INSERT INTO shop_coupon (code, description, discount_type, discount_value, min_order, max_usage, max_usage_per_user, usage_type, specific_email, is_active, expires_at)
        VALUES ('QHUN22', 'Voucher cho thành viên mới', 'percent', 10, 0, 0, 1, 'all', NULL, 1, NULL)
    """)
    print("[OK] Created QHUN22 coupon")
    
    # Get the new coupon ID
    cursor.execute("SELECT id FROM shop_coupon WHERE code = 'QHUN22'")
    new_id = cursor.fetchone()[0]
    print(f"    Coupon ID: {new_id}")

conn.commit()

# Verify
cursor.execute("SELECT id, code, discount_value, is_active FROM shop_coupon WHERE code = 'QHUN22'")
coupon = cursor.fetchone()
print(f"\n[INFO] QHUN22 Coupon details:")
print(f"  - ID: {coupon[0]}")
print(f"  - Code: {coupon[1]}")
print(f"  - Discount: {coupon[2]}%")
print(f"  - Active: {coupon[3]}")

conn.close()
print("\nDone!")

