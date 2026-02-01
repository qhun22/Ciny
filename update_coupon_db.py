import sqlite3
import sys

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Connect to the database directly
db_path = r'D:\Py\Ciny\db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Remove max_discount column and add new columns
try:
    cursor.execute("ALTER TABLE shop_coupon RENAME COLUMN max_discount TO max_usage")
    print("[OK] Renamed 'max_discount' to 'max_usage'")
except sqlite3.OperationalError as e:
    print(f"[X] Rename max_discount: {e}")
    
    # If max_discount doesn't exist, try adding max_usage directly
    try:
        cursor.execute("ALTER TABLE shop_coupon ADD COLUMN max_usage INTEGER DEFAULT 0")
        print("[OK] Added 'max_usage' column")
    except sqlite3.OperationalError as e2:
        print(f"[X] Add max_usage: {e2}")

try:
    cursor.execute("ALTER TABLE shop_coupon ADD COLUMN max_usage_per_user INTEGER DEFAULT 1")
    print("[OK] Added 'max_usage_per_user' column")
except sqlite3.OperationalError as e:
    print(f"[X] Add max_usage_per_user: {e}")

conn.commit()

# Verify columns
cursor.execute("PRAGMA table_info(shop_coupon)")
columns = cursor.fetchall()
print("\nCurrent columns in shop_coupon:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
print("\nDone!")

