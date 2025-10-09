from .schemas import car_schema, cars_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Car, db, Customer
from . import cars_bp
from app.helpers import get_or_404, load_request_data

@cars_bp.route('/', methods=['POST'])
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


@cars_bp.route('/', methods=['GET'])
def get_cars():
  cars = db.session.execute(select(Car)).scalars().all()
  return cars_schema.jsonify(cars), 200
  

@cars_bp.route('/<car_vin>', methods=['GET'])
def get_car(car_id):
  car = get_or_404(Car, car_id)
  return car_schema.jsonify(car), 200


@cars_bp.route('/<car_vin>', methods=['PUT'])
def edit_car(car_vin):
  car = get_or_404(Car, car_vin)
  car_data = load_request_data(car_schema)
  for key, value in car_data.items():
    if hasattr(Car, key):
      setattr(Car, key, value)
  db.session.commit()
  return car_schema.jsonify(car), 200


@cars_bp.route('/<car_vin>', methods=['DELETE'])
def delete_car(car_vin):
  car = get_or_404(Car, car_vin)
  db.session.delete(car)
  db.session.commit()
  return jsonify({'message': 'Successfully deleted car'}), 200
      
  