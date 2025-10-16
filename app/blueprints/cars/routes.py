from .schemas import car_schema, cars_schema, car_schema_dict
from . import cars_bp
from flask import request, jsonify
from sqlalchemy import select
from app.models import Car, db, Customer
from app.utils.helpers import get_or_404, load_request_data, update_field_values, paginate, check_role
from app.utils.jwt_utils import token_required
from app.extensions import limiter, cache

# Create Car
@cars_bp.route('/', methods=['POST'])
@limiter.limit('5 per minute')
@token_required
def create_car(user, role):
  check_role(role, ('customer', 'mechanic'))
  car_data = request.get_json()
  # Check if car with this vin already exists (no duplicates allowed)
  car_existing = db.session.execute(select(Car).where(Car.vin == car_data['vin'])).scalars().first()
  if car_existing:
    return jsonify({'message': f"A car with VIN #{car_data['vin']}  already exists."}), 400
  
  if role == 'customer':
    car_data.pop('customer', None)
    car = car_schema.load(car_data)
    car.customer_id = user.id
  else:
    car = car_schema.load(car_data)
    # Check if customer exists
    customer_id = car.customer_id
    get_or_404(Customer, customer_id)

  db.session.add(car)
  db.session.commit()
  return car_schema.jsonify(car), 201


# Get All Cars' Data
@cars_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
@token_required
def get_cars(user, role):
  check_role(role, 'mechanic')
  cars = paginate(select(Car), cars_schema)
  return jsonify(cars['items']), 200
  

# Get Single Car Data
@cars_bp.route('/<car_vin>', methods=['GET'])
@cache.cached(timeout=60)
@token_required
def get_car(user, role, car_vin):
  check_role(role, ('customer', 'mechanic'))
  car = db.session.execute(select(Car).where(Car.vin == car_vin)).scalars().first()
  if not car:
    return jsonify({'message': f'Car with VIN {car_vin} not found'}), 404
  
  if role == 'mechanic':
    pass
  elif role == 'customer':
    if not any(car.vin == car_vin for car in user.cars):
      return jsonify({'message': f'Car with VIN {car_vin} not found'}), 404
  else:
    return jsonify({'message': 'Invalid role'}), 401
  
  return car_schema.jsonify(car), 200

    
# Edit Car Data
@cars_bp.route('/<car_vin>', methods=['PUT', 'PATCH'])
@limiter.limit('5 per minute')
@token_required
def edit_car(user, role, car_vin):
  check_role(role, ('customer', 'mechanic'))
  car = db.session.execute(select(Car).where(Car.vin == car_vin)).scalars().first()
  if not car:
    return jsonify({'message': f'Car with VIN {car_vin} not found'}), 404
  
  if role == 'mechanic':
    pass
  elif role == 'customer':
    if not any(car.vin == car_vin for car in user.cars):
      return jsonify({'message': f'Car with VIN {car_vin} not found <3'}), 404
  else:
    return jsonify({'message': 'Invalid role'}), 401
  
  car_data = load_request_data(
    schema=car_schema_dict,
    model_class=Car,
    partial=(request.method == 'PATCH'))
  update_field_values(car, car_data)
  db.session.commit()
  return car_schema.jsonify(car), 200
  


# Delete Car
@cars_bp.route('/<car_vin>', methods=['DELETE'])
@limiter.limit('5 per minute')
@token_required
def delete_car(user, role, car_vin):
  
  car = get_or_404(Car, car_vin)
  db.session.delete(car)
  db.session.commit()
  return jsonify({'message': 'Successfully deleted car'}), 200
      
  