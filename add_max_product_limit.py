import sqlite3

# Thêm cột max_product_limit vào bảng shop_coupon
conn = sqlite3.connect('D:\\Py\\Ciny\\db.sqlite3')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE shop_coupon ADD COLUMN max_product_limit INTEGER NOT NULL DEFAULT 0")
    print("SUCCESS: Da them cot max_product_limit vao bang shop_coupon")
except Exception as e:
    print(f"ERROR: {e}")

conn.commit()
conn.close()
