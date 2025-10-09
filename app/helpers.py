from . import db
from flask import abort, request, jsonify
from marshmallow import ValidationError

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