from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, os, hashlib, hmac, secrets, shutil
from datetime import datetime, timedelta
import jwt

DB_PATH = os.path.join(os.path.dirname(__file__), 'fms.db')
SECRET_KEY = os.environ.get('FMS_SECRET_KEY', 'replace-this-with-a-secure-key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')

app = FastAPI(title='FMS Backend (Azure-ready)')

origins = ['*']
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def hash_password(password: str, iterations: int = 150_000) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return f"{iterations}${salt.hex()}${dk.hex()}"

def verify_password(stored_hash: str, password: str) -> bool:
    try:
        parts = stored_hash.split('$')
        iterations = int(parts[0])
        salt = bytes.fromhex(parts[1])
        stored = parts[2]
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return hmac.compare_digest(dk.hex(), stored)
    except Exception:
        return False

def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire.isoformat()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

@app.post('/signup', status_code=201)
def signup(payload: dict):
    email = payload.get('email')
    password = payload.get('password')
    name = payload.get('name', 'User')
    role = payload.get('role', 'accountant')
    if not email or not password:
        raise HTTPException(status_code=400, detail='email and password required')

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail='user already exists')
    ph = hash_password(password)
    cur.execute('INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)', (name, email, ph, role))
    conn.commit()
    cur.execute('SELECT user_id, name, email, role FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    return dict(row)

@app.post('/token')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    password = form_data.password
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cur.fetchone()
    conn.close()
    if not user or not verify_password(user['password_hash'], password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
    token = create_access_token({'sub': user['email'], 'role': user['role']})
    return {'access_token': token, 'token_type': 'bearer'}

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail='Invalid authentication credentials')
    email = payload.get('sub')
    if not email:
        raise HTTPException(status_code=401, detail='Invalid token payload')
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute('SELECT user_id, name, email, role FROM users WHERE email = ?', (email,))
    user = cur.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return dict(user)

def require_role(allowed_roles):
    def _inner(user = Depends(get_current_user)):
        if user['role'] not in allowed_roles:
            raise HTTPException(status_code=403, detail='Insufficient permissions')
        return user
    return _inner

@app.post('/upload/logo', dependencies=[Depends(require_role(['admin','accountant']))])
async def upload_logo(file: UploadFile = File(...), user = Depends(get_current_user)):
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'logos')
    os.makedirs(uploads_dir, exist_ok=True)
    filename = f"{user['email']}_{file.filename}"
    path = os.path.join(uploads_dir, filename)
    with open(path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    return {'filename': filename, 'path': path}

# include exports router if available
try:
    from exports import router as exports_router
    app.include_router(exports_router)
except Exception:
    pass

@app.get('/health')
def health():
    return {'status':'ok'}
