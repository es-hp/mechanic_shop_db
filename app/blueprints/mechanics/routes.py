from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db
from . import mechanics_bp
from app.utils.helpers import get_or_404, load_request_data, paginate
from app.extensions import limiter, cache


# Create Mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit('5 per minute')
def create_mechanic():
  mechanic_data = load_request_data(mechanic_schema)  
  query = select(Mechanic).where(Mechanic.phone == mechanic_data['phone'])
  mechanic_existing = db.session.execute(query).scalars().all()
  if mechanic_existing:
    return jsonify({'message': 'A mechanic with this phone number already exists.'}), 400
  new_mechanic = Mechanic(**mechanic_data)
  db.session.add(new_mechanic)
  db.session.commit()
  return mechanic_schema.jsonify(new_mechanic), 201


# Get All Mechanics' Data
@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
  query = select(Mechanic).order_by(Mechanic.name)
  mechanics = paginate(query, mechanics_schema)
  return jsonify(mechanics['items']), 200


# Get Single Mechanic Data
@mechanics_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit('10 per minute')
def edit_mechanic(id):
  mechanic = get_or_404(Mechanic, id)
  mechanic_data = load_request_data(mechanic_schema)  
  for key, value in mechanic_data.items():
    if hasattr(mechanic, key):
      setattr(mechanic, key, value)
  db.session.commit()
  return mechanic_schema.jsonify(mechanic), 200
  

# Delete Mechanic
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit('3 per minute')
def delete_mechanic(id):
  mechanic = get_or_404(Mechanic, id)
  db.session.delete(mechanic)
  db.session.commit()
  return jsonify({'message': 'Successfully deleted mechanic'}), 200