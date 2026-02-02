import sqlite3
import sys

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
    print(f"[OK] User: {user[1]} (ID: {user[0]})")
    
    # Check profile
    cursor.execute("SELECT id, phone_number, is_phone_verified FROM shop_userprofile WHERE user_id = ?", (user[0],))
    profile = cursor.fetchone()
    if profile:
        print(f"    Phone: {profile[1]}, Verified: {profile[2]}")
    
    # Check and remove QHUN22 voucher if user hasn't verified
    if profile and profile[2] == 0:
        cursor.execute("""
            DELETE FROM shop_uservoucher 
            WHERE user_id = ? AND coupon_id = (
                SELECT id FROM shop_coupon WHERE code = 'QHUN22'
            )
        """, (user[0],))
        conn.commit()
        print("    [OK] Removed QHUN22 voucher (user hasn't verified phone)")
        print("    User needs to verify phone to receive voucher!")
    else:
        print("    User has verified phone, keeping voucher")
else:
    print("[X] User uyenvy@gmail.com not found!")

conn.close()
print("\nDone!")


