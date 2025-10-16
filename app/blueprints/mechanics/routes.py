from .schemas import mechanic_schema, mechanics_schema, mechanic_schema_dict
from flask import request, jsonify
from sqlalchemy import select
from app.models import Mechanic, db
from . import mechanics_bp
from app.utils.helpers import load_request_data, update_field_values, paginate, handle_login, check_role
from app.utils.jwt_utils import token_required
from app.extensions import limiter, cache



# Mechanic Login
@mechanics_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def mechanic_login():
  return handle_login(Mechanic, 'mechanic')


# Create Mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit('5 per minute')
@token_required
def create_mechanic(user, role):
  check_role(role, 'mechanic')
  new_mechanic = load_request_data(mechanic_schema, Mechanic)  
  query = select(Mechanic).where(Mechanic.phone == new_mechanic.phone)
  mechanic_existing = db.session.execute(query).scalars().all()
  if mechanic_existing:
    return jsonify({'message': 'A mechanic with this phone number already exists.'}), 400
  db.session.add(new_mechanic)
  db.session.commit()
  return mechanic_schema.jsonify(new_mechanic), 201


# Get All Mechanics' Data
@mechanics_bp.route('/', methods=['GET'])
# @cache.cached(timeout=1)
@token_required
def get_mechanics(user, role):
  check_role(role, 'mechanic')
  sort = request.args.get('sort') or 'name'
  *rest, ticket_count_col, _, base_query = Mechanic.get_ticket_counts()
  if sort == 'ticket_count':
    query = base_query.order_by(ticket_count_col.desc())
  elif sort == 'salary':
    query = base_query.order_by(Mechanic.salary.desc())
  else:
    query = base_query.order_by(Mechanic.name)
  mechanics = paginate(query, mechanics_schema)
  return jsonify(mechanics['items']), 200

# query = select(Mechanic).order_by(Mechanic.salary.desc())


# Get Single Mechanic Data 
@mechanics_bp.route("/my-account", methods=['GET'])
@cache.cached(timeout=60)
@token_required
def get_customer(user, role):
  check_role(role, 'mechanic')
  _, mechanics, *rest = Mechanic.get_ticket_counts()
  mechanic = next((m for m in mechanics if m.id == user.id), None)
  return mechanic_schema.jsonify(mechanic), 200  


# Edit Mechanic Data
@mechanics_bp.route('/my-account', methods=['PUT', 'PATCH'])
@limiter.limit('10 per minute')
@token_required
def edit_mechanic(user, role):
  check_role(role, 'mechanic')
  mechanic_data = load_request_data(
    schema=mechanic_schema_dict,
    model_class=Mechanic,
    partial=(request.method == 'PATCH')
  )
  update_field_values(user, mechanic_data)
  db.session.commit()
  return mechanic_schema.jsonify(user), 200
  

# Delete Mechanic
@mechanics_bp.route('/my-account', methods=['DELETE'])
@limiter.limit('3 per minute')
@token_required
def delete_mechanic(user, role):
  check_role(role, 'mechanic')
  db.session.delete(user)
  db.session.commit()
  return jsonify({'message': 'Successfully deleted mechanic'}), 200