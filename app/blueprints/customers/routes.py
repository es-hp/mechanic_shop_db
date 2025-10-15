from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from . import customers_bp
from app.utils.helpers import get_or_404, load_request_data, paginate
from app.utils.jwt_utils import encode_token, token_required
from app.extensions import limiter, cache
from typing import Dict, Any, cast

# Login
@customers_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def login():
  try:
    # Kept getting pylance error without forcing it to always be a dict
    credentials = cast(Dict[str, Any], login_schema.load(request.get_json(force=True)))
    email = credentials['email']
    password = credentials['password']
  except ValidationError as e:
    return jsonify({'message': e.messages}), 400
  query = select(Customer).where(Customer.email == email)
  customer = db.session.execute(query).scalar_one_or_none()
  if not customer or customer.password != password:
    return jsonify({'message': 'Invalid email or password'}), 401
  auth_token = encode_token(customer.id, role='customer')
  response = {
    'status': 'success',
    'message': 'Successfully logged in',
    'auth_token': auth_token
  }
  return jsonify(response), 200


# Create Customer
@customers_bp.route("/", methods=['POST'])
@limiter.limit('5 per minute')
def create_customer():
  customer_data = load_request_data(customer_schema)
  query = select(Customer).where(Customer.email == customer_data['email'])
  customer_existing = db.session.execute(query).scalars().all()
  if customer_existing:
    return jsonify ({"message": "A customer with this email already exists."}), 400
  new_customer = Customer(**customer_data)
  db.session.add(new_customer)
  db.session.commit()
  return customer_schema.jsonify(new_customer), 201


# Get All Customers' Data
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=30)
def get_customers():
  query = select(Customer).order_by(Customer.name)
  customers = paginate(query, customers_schema)
  return jsonify(customers['items']), 200


# Get Single Customer Data 
@customers_bp.route("/my-account", methods=['GET'])
@cache.cached(timeout=60)
@token_required
def get_customer(customer_id):
  customer = get_or_404(Customer, customer_id)
  return customer_schema.jsonify(customer), 200


# Edit Customer Data
@customers_bp.route("/", methods=['PUT', 'PATCH'])
@limiter.limit('5 per minute')
@token_required
def edit_customer(customer_id):
  partial = request.method == 'PATCH'
  customer = get_or_404(Customer, customer_id)
  customer_data = load_request_data(customer_schema, partial=partial)  
  for key, value in customer_data.items():
    if hasattr(customer, key):
      setattr(customer, key, value)
  db.session.commit()
  return customer_schema.jsonify(customer), 200


# Delete Customer
@customers_bp.route("/", methods=['DELETE'])
@limiter.limit('3 per minute')
@token_required
def delete_customer(customer_id):
  customer = get_or_404(Customer, customer_id)
  db.session.delete(customer)
  db.session.commit()
  return jsonify({"message": f"Successfully deleted customer {customer.name}"}), 200
