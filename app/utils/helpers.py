from .. import db
from flask import abort, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from werkzeug.exceptions import NotFound
from app.utils.jwt_utils import encode_token
from app.blueprints.authentication.schemas import login_schema
from typing import Dict, cast, Any, Type, TypeVar



def handle_http_exception(e):
  response = e.get_response()
  response.data = jsonify({'error': e.name, 'message': e.description, 'code': e.code}).data
  response.content_type = 'application/json'
  return response


def get_or_404(model, obj_id, name="Requested object"):
  name = name or model.__name__
  obj = db.session.get(model, obj_id)
  if not obj:
    abort(404, description=f'{name} not found')
  return obj

T = TypeVar('T')

def load_request_data(schema, model_class: Type[T], partial=False) -> T:
  try:
    return cast(T, schema.load(request.get_json(), partial=partial))
  except ValidationError as e:
    abort(400, description=e.messages)
  

def update_field_values(obj, data):
  for key, value in data.items():
    if hasattr(obj, key):
      setattr(obj, key, value)
  
    
def paginate(query, schema):
  try:
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    results = db.paginate(query, page=page, per_page=per_page)
  except ValueError:
    abort(400, description='Invalid page or per_page value')
  except NotFound:
    abort(404, description='Page not found')
  return {
    'items': schema.dump(results.items),
    'total': results.total,
    'page': results.page,
    'pages': results.pages
  }
  
  
def handle_login(model, role):
  try:
    # Kept getting pylance error without specifying type
    login_info = cast(Dict[str, Any], login_schema.load(request.get_json(force=True)))
    email = login_info['email']
    password = login_info['password']
  except ValidationError as e:
    return jsonify({'message': e.messages}), 400
  query = select(model).where(model.email == email)
  user = db.session.execute(query).scalar_one_or_none()
  if not user or user.password != password:
    return jsonify({'message': 'Invalid email or password'}), 401
  auth_token = encode_token(user.id, role=role)
  response = {
    'status': 'success',
    'message': 'Successfully logged in',
    'auth_token': auth_token
  }
  return jsonify(response), 200


def check_role(user_role, req_role):
  if isinstance(req_role, (list, tuple, set)):
    if user_role not in req_role:
      abort(403, description='Access denied')
  else:
    if user_role != req_role:
      abort(403, description='Access denied')
  return None