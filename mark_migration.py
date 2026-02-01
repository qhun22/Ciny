import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Mark migration as applied
cursor.execute("INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('shop', '0009_feedback', datetime('now'))")
conn.commit()

print('Migration marked as applied!')
conn.close()



