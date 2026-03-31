import bcrypt
try:
    password = "testpassword".encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print(f"Hashed: {hashed}")
    matches = bcrypt.checkpw(password, hashed)
    print(f"Matches: {matches}")
except Exception as e:
    print(f"Error: {e}")
