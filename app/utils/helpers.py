from .. import db
from flask import abort, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from werkzeug.exceptions import NotFound

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


def load_request_data(schema):
  try:
    return schema.load(request.get_json())
  except ValidationError as e:
    abort(400, description=e.messages)
    
    
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