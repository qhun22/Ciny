"""
Check all coupons and orders.
"""
import sqlite3

db_path = r"D:\Py\Ciny\db.sqlite3"

def run_sql():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 1. All Coupons ===")
    cursor.execute("SELECT id, code, is_active, usage_type FROM shop_coupon ORDER BY id")
    for row in cursor.fetchall():
        print(f"ID={row[0]}, Code={row[1]}, Active={row[2]}, Type={row[3]}")
    
    print("\n=== 2. All Orders with coupon_code ===")
    cursor.execute("""
        SELECT id, user_id, coupon_code, total, created_at 
        FROM shop_order
        WHERE coupon_code IS NOT NULL AND coupon_code != ''
        ORDER BY id
    """)
    for row in cursor.fetchall():
        print(f"Order #{row[0]}, User={row[1]}, Coupon='{row[2]}', Total={row[3]}, Date={row[4]}")
    
    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    run_sql()

