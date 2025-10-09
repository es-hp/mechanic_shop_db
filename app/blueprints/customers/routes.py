from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from . import customers_bp


# Create Customer
@customers_bp.route("/", methods=['POST'])
def create_customer():
  try:
    customer_data = customer_schema.load(request.get_json())
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  query = select(Customer).where(Customer.email == customer_data['email'])
  customer_existing = db.session.execute(query).scalars().all()
  if customer_existing:
    return jsonify ({"message": "A customer with this email already exists."}), 400
  new_customer = Customer(**customer_data)
  db.session.add(new_customer)
  db.session.commit()
  return customer_schema.jsonify(new_customer), 201


# Get All Customers
@customers_bp.route('/', methods=['GET'])
def get_customers():
  query = select(Customer)
  customers = db.session.execute(query).scalars().all()
  return customers_schema.jsonify(customers), 200


# Get Single Customer Data  
@customers_bp.route("/<int:id>", methods=['GET'])
def get_customer(id):
  customer = db.session.get(Customer, id)
  return customer_schema.jsonify(customer), 200


# Edit Customer Data
@customers_bp.route("/<int:id>", methods=['PUT'])
def edit_customer(id):
  customer = db.session.get(Customer, id)
  if not customer:
    return jsonify({"message": "Invalid customer id"}), 400
  
  try:
    customer_data = customer_schema.load(request.get_json())
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  for key, value in customer_data.items():
    if hasattr(customer, key):
      setattr(customer, key, value)
  db.session.commit()
  return customer_schema.jsonify(customer), 200


# Delete Customer
@customers_bp.route("/<int:id>", methods=['DELETE'])
def delete_customer(id):
  customer = db.session.get(Customer, id)
  if not customer:
    return jsonify({"message": "Invalid customer id"}), 400
  db.session.delete(customer)
  db.session.commit()
  return jsonify({"message": f"Successfully deleted user {id}"}), 200
