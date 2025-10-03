import sqlite3, os, argparse, secrets, hashlib
def hash_password(password: str, iterations: int = 150_000) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return f"{iterations}${salt.hex()}${dk.hex()}"
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--email', required=True)
    p.add_argument('--password', required=True)
    p.add_argument('--name', default='Admin')
    p.add_argument('--role', default='admin')
    args = p.parse_args()
    db_path = os.path.join(os.path.dirname(__file__), 'fms.db')
    if not os.path.exists(db_path):
        print('DB not found at', db_path)
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (args.email,))
    if cur.fetchone():
        print('User already exists with that email.')
        conn.close()
        return
    ph = hash_password(args.password)
    cur.execute('INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)', (args.name, args.email, ph, args.role))
    conn.commit()
    conn.close()
    print('Created admin user', args.email)
if __name__ == '__main__':
    main()
