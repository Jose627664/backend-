from fastapi import HTTPException, Header, Cookie, Request
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
import os
from models import User, UserSession

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'afrolatino_secret_key_12345')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '10080'))  # 7 days

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user_id: str) -> str:
    """Create a JWT token"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        'user_id': user_id,
        'exp': expire
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get('user_id')
        if user_id is None:
            raise HTTPException(status_code=401, detail='Invalid authentication')
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid authentication')

async def get_current_user(db, authorization: Optional[str] = Header(None), session_token: Optional[str] = Cookie(None)):
    """
    Get current user from JWT token or session token
    Tries: 1) Cookie session_token, 2) Authorization header
    """
    token = None
    
    # Try cookie first
    if session_token:
        token = session_token
    # Then try Authorization header
    elif authorization and authorization.startswith('Bearer '):
        token = authorization.split(' ')[1]
    
    if not token:
        raise HTTPException(status_code=401, detail='Not authenticated')
    
    # Check if it's a session token or JWT
    # Session tokens from Google OAuth are longer
    if len(token) > 200:
        # This is a session token from Google OAuth
        session = await db.user_sessions.find_one({'session_token': token}, {'_id': 0})
        if not session:
            raise HTTPException(status_code=401, detail='Session not found')
        
        # Check expiration
        expires_at = session['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail='Session expired')
        
        user_id = session['user_id']
    else:
        # This is a JWT token
        user_id = verify_token(token)
    
    # Get user
    user = await db.users.find_one({'user_id': user_id}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    
    return User(**user)

async def get_current_admin(db, authorization: Optional[str] = Header(None), session_token: Optional[str] = Cookie(None)):
    """Get current user and verify admin status"""
    user = await get_current_user(db, authorization, session_token)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail='Admin access required')
    return user
