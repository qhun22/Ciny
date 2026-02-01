import sqlite3
import codecs
import sys

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Connect to the database directly
db_path = r'D:\Py\Ciny\db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add new columns to shop_coupon table
try:
    cursor.execute("ALTER TABLE shop_coupon ADD COLUMN description TEXT DEFAULT ''")
    print("[OK] Added 'description' column")
except sqlite3.OperationalError as e:
    print(f"[X] 'description' column: {e}")

try:
    cursor.execute("ALTER TABLE shop_coupon ADD COLUMN usage_type VARCHAR(10) DEFAULT 'all'")
    print("[OK] Added 'usage_type' column")
except sqlite3.OperationalError as e:
    print(f"[X] 'usage_type' column: {e}")

try:
    cursor.execute("ALTER TABLE shop_coupon ADD COLUMN specific_email VARCHAR(254) NULL")
    print("[OK] Added 'specific_email' column")
except sqlite3.OperationalError as e:
    print(f"[X] 'specific_email' column: {e}")

conn.commit()

# Verify columns
cursor.execute("PRAGMA table_info(shop_coupon)")
columns = cursor.fetchall()
print("\nCurrent columns in shop_coupon:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
print("\nDone!")
