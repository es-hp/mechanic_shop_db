from .schemas import car_schema, cars_schema
from flask import request, jsonify
from sqlalchemy import select
from app.models import Car, db, Customer
from . import cars_bp
from app.utils.helpers import get_or_404, load_request_data, paginate
from app.extensions import limiter, cache

# Create Car
@cars_bp.route('/', methods=['POST'])
@limiter.limit('5 per minute')
def create_car():
  # Check request (validate)
  car_data = load_request_data(car_schema)
  # Check if customer exists
  customer_id = car_data['customer_id']
  get_or_404(Customer, customer_id)
  # Check for car duplicate
  car_existing = db.session.scalar(select(Car).where(Car.vin == car_data['vin']))
  if car_existing:
    return jsonify({'message': f'A car with VIN #{car_data['vin']}  already exists.'}), 400
  # Create new car instance
  new_car = Car(**car_data)
  db.session.add(new_car)
  db.session.commit()
  return car_schema.jsonify(new_car), 201


# Get All Cars' Data
@cars_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_cars():
  cars = paginate(select(Car), cars_schema)
  return jsonify(cars['items']), 200
  

# Get Single Car Data
@cars_bp.route('/<car_vin>', methods=['GET'])
@cache.cached(timeout=60)
def get_car(car_vin):
  car = get_or_404(Car, car_vin)
  return car_schema.jsonify(car), 200


# Edit Car Data
@cars_bp.route('/<car_vin>', methods=['PUT'])
@limiter.limit('5 per minute')
def edit_car(car_vin):
  car = get_or_404(Car, car_vin)
  car_data = load_request_data(car_schema)
  for key, value in car_data.items():
    if hasattr(Car, key):
      setattr(Car, key, value)
  db.session.commit()
  return car_schema.jsonify(car), 200


# Delete Car
@cars_bp.route('/<car_vin>', methods=['DELETE'])
@limiter.limit('5 per minute')
def delete_car(car_vin):
  car = get_or_404(Car, car_vin)
  db.session.delete(car)
  db.session.commit()
  return jsonify({'message': 'Successfully deleted car'}), 200
      
  