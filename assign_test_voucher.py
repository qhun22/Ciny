import sqlite3
import sys
from datetime import datetime

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Connect to the database
db_path = r'D:\Py\Ciny\db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check user uyenvy@gmail.com
cursor.execute("SELECT id, username, email FROM auth_user WHERE email = ?", ('uyenvy@gmail.com',))
user = cursor.fetchone()

if user:
    print(f"[OK] User: {user[1]} (ID: {user[0]})")
    
    # Check TEST coupon
    cursor.execute("SELECT id, code, usage_type, specific_email FROM shop_coupon WHERE code = 'TEST'")
    test_coupon = cursor.fetchone()
    
    if test_coupon:
        print(f"    Coupon: {test_coupon[1]} (ID: {test_coupon[0]})")
        print(f"    Usage type: {test_coupon[2]}, Email: {test_coupon[3]}")
        
        # Check if user already has this coupon
        cursor.execute("SELECT id FROM shop_uservoucher WHERE user_id = ? AND coupon_id = ?", (user[0], test_coupon[0]))
        has_voucher = cursor.fetchone()
        
        if has_voucher:
            print(f"    User already has this voucher (ID: {has_voucher[0]})")
        else:
            # Assign voucher to user
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO shop_uservoucher (user_id, coupon_id, created_at) VALUES (?, ?, ?)", 
                          (user[0], test_coupon[0], now))
            conn.commit()
            print(f"    [OK] Assigned TEST voucher to user!")
    else:
        print("    [X] TEST coupon not found!")
else:
    print("[X] User uyenvy@gmail.com not found!")

conn.close()
print("\nDone!")


