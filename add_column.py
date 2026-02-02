import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.db import connection

cursor = connection.cursor()
cursor.execute("ALTER TABLE shop_review ADD COLUMN is_anonymous BOOLEAN DEFAULT 0")
print("Added is_anonymous column successfully!")

