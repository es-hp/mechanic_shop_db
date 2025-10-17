from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
import os
from dotenv import load_dotenv
from functools import wraps
from flask import request, jsonify
from app.models import Customer, Mechanic

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY') or 'secret-key-string'

def encode_token(user_id, role):
  payload = {
    'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
    'iat': datetime.now(timezone.utc),
    'sub': str(user_id),
    'role': str(role)
  }
  
  token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
  return token

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None
    if 'Authorization' in request.headers:
      token = request.headers['Authorization'].split(' ')[1]
    if not token:
      return jsonify({'message': 'Token is missing'}), 401
    # Decode the token
    try:
      data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
      user_id = data.get('sub')
      role = data.get('role')
      
      if not user_id or not role:
        return jsonify({'message': 'Invalid token'}), 401
      
      try:
        user_id = int(user_id)
      except ValueError:
        return jsonify({'message': 'Invalid ID format'}), 401
      
      from app.utils.helpers import get_or_404
      if role == 'customer':
        user = get_or_404(Customer, user_id)
      elif role == 'mechanic':
        user = get_or_404(Mechanic, user_id)
      else:
        return jsonify({'message': 'Invalid role'}), 401
        
    except jose.exceptions.ExpiredSignatureError:
      return jsonify({'message': 'Token has expired'}), 401
    except jose.exceptions.JWTError:
      return jsonify({'message': 'Invalid token'}), 401
    return f(user, role, *args, **kwargs)
  return decorated