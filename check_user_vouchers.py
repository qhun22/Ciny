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
cursor.execute("SELECT id, username, email FROM auth_user WHERE email = 'uyenvy@gmail.com'")
user = cursor.fetchone()

if user:
    print(f"[OK] User found: {user[1]} (ID: {user[0]}, Email: {user[2]})")
    
    # Check UserProfile
    cursor.execute("SELECT id, phone_number, is_phone_verified FROM shop_userprofile WHERE user_id = ?", (user[0],))
    profile = cursor.fetchone()
    if profile:
        print(f"    Profile ID: {profile[0]}, Phone: {profile[1]}, Verified: {profile[2]}")
    else:
        print("    No profile found!")
    
    # Check vouchers for this user
    cursor.execute("""
        SELECT uv.id, c.code, c.discount_value, c.discount_type, c.expires_at 
        FROM shop_uservoucher uv
        JOIN shop_coupon c ON uv.coupon_id = c.id
        WHERE uv.user_id = ?
    """, (user[0],))
    user_vouchers = cursor.fetchall()
    
    if user_vouchers:
        print(f"    User has {len(user_vouchers)} voucher(s):")
        for uv in user_vouchers:
            print(f"      - {uv[1]}: {uv[2]}{'%' if uv[3] == 'percent' else 'đ'}{f' (exp: {uv[4]})' if uv[4] else ' (vô thời hạn)'}")
    else:
        print("    User has no vouchers!")
        
        # Check QHUN22 coupon
        cursor.execute("SELECT id FROM shop_coupon WHERE code = 'QHUN22'")
        qhun22 = cursor.fetchone()
        if qhun22:
            # Assign QHUN22 to user with created_at
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO shop_uservoucher (user_id, coupon_id, created_at) VALUES (?, ?, ?)", 
                          (user[0], qhun22[0], now))
            conn.commit()
            print(f"    [OK] Assigned QHUN22 voucher to user")
        else:
            print("    [X] QHUN22 coupon not found!")
else:
    print("[X] User uyenvy@gmail.com not found!")

conn.close()
print("\nDone!")
