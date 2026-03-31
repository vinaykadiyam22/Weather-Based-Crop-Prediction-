import sqlite3

db_path = 'backend/crop_advisory.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cursor.fetchall()]
print(f"Current columns: {columns}")

# Columns to add
to_add = [
    ("is_admin", "BOOLEAN DEFAULT 0"),
    ("is_active", "BOOLEAN DEFAULT 1"),
    ("farm_size", "FLOAT"),
    ("farming_experience", "INTEGER"),
    ("preferred_crops", "JSON"),
    ("created_at", "DATETIME"),
    ("last_login", "DATETIME")
]

for col_name, col_type in to_add:
    if col_name not in columns:
        print(f"Adding column {col_name}...")
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        except Exception as e:
            print(f"Error adding {col_name}: {e}")

conn.commit()
conn.close()
print("Migration complete.")
