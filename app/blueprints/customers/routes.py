from .schemas import customer_schema, customers_schema, customer_schema_dict
from flask import request, jsonify
from sqlalchemy import select
from app.models import Customer, db
from . import customers_bp
from app.utils.helpers import load_request_data, get_or_404, update_field_values, paginate, handle_login, check_role
from app.utils.jwt_utils import token_required
from app.extensions import limiter, cache


# Customer Login
@customers_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def customer_login():
  return handle_login(Customer, 'customer')


# Create Customer
@customers_bp.route("/", methods=['POST'])
@limiter.limit('5 per minute')
def create_customer():
  new_customer = load_request_data(customer_schema, Customer)
  query = select(Customer).where(Customer.email == new_customer.email)
  customer_existing = db.session.execute(query).scalars().all()
  if customer_existing:
    return jsonify ({"message": "A customer with this email already exists."}), 409
  db.session.add(new_customer)
  db.session.commit()
  return customer_schema.jsonify(new_customer), 201


# Get All Customers' Data
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=1)
@token_required
def get_customers(user, role):
  check_role(role, 'mechanic')
  query = select(Customer).order_by(Customer.name)
  customers = paginate(query, customers_schema)
  return jsonify(customers['items']), 200


# Get Single Customer Data 
@customers_bp.route("/account", methods=['GET'])
@cache.cached(timeout=1)
@token_required
def get_customer(user, role):
  check_role(role, ('customer', 'mechanic'))
  if role == 'customer':
    customer = user
  elif role == 'mechanic':
    customer_id = request.args.get('customer_id', type=int)
    if customer_id is None:
      return jsonify({'message': "Missing or invalid required parameter 'customer_id'"}), 400
    
    customer = get_or_404(Customer, customer_id)  
  return customer_schema.jsonify(customer), 200


# Edit Customer Data
@customers_bp.route("/", methods=['PUT', 'PATCH'])
@limiter.limit('5 per minute')
@token_required
def edit_customer(user, role):
  check_role(role, 'customer')
  # Using load_request_data for validation only
  customer_data = load_request_data(
    schema=customer_schema_dict, 
    model_class=Customer,
    partial=(request.method == 'PATCH')
  )
  update_field_values(user, customer_data)
  db.session.commit()
  return customer_schema.jsonify(user), 200


# Delete Customer
@customers_bp.route("/", methods=['DELETE'])
@limiter.limit('3 per minute')
@token_required
def delete_customer(user, role):
  check_role(role, 'customer')
  db.session.delete(user)
  db.session.commit()
  return jsonify({"message": "Successfully deleted your account."}), 200
