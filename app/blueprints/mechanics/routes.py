from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db
from . import mechanics_bp
from app.helpers import get_or_404, load_request_data

@mechanics_bp.route('/', methods=['POST'])
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


@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
  query = select(Mechanic)
  mechanics = db.session.execute(query).scalars().all()
  return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route('/<int:id>', methods=['PUT'])
def edit_mechanic(id):
  mechanic = get_or_404(Mechanic, id)
  mechanic_data = load_request_data(mechanic_schema)  
  for key, value in mechanic_data.items():
    if hasattr(mechanic, key):
      setattr(mechanic, key, value)
  db.session.commit()
  return mechanic_schema.jsonify(mechanic), 200
  

@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
  mechanic = get_or_404(Mechanic, id)
  db.session.delete(mechanic)
  db.session.commit()
  return jsonify({'message': 'Successfully deleted mechanic'}), 200