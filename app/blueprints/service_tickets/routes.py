from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from sqlalchemy import select
from app.models import ServiceTicket, db, Mechanic, Customer, Car
from . import service_tickets_bp
from app.utils.helpers import get_or_404, load_request_data, paginate
from app.utils.jwt_utils import token_required
from app.extensions import limiter, cache


# Create service ticket
@service_tickets_bp.route('/', methods=['POST'])
@limiter.limit('10 per minute')
def create_service_ticket():
  service_ticket_data = load_request_data(service_ticket_schema)
  car = db.session.get(Car, service_ticket_data['car_vin'])
  if not car:
    return jsonify({'message': 'Car not found'}), 404
  new_service_ticket = ServiceTicket(**service_ticket_data)
  db.session.add(new_service_ticket)
  db.session.commit()
  return service_ticket_schema.jsonify(new_service_ticket), 201
  

# Add mechanic to service ticket
@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit('10 per minute')
def assign_mechanic(ticket_id, mechanic_id):
  mechanic = get_or_404(Mechanic, mechanic_id)
  service_ticket = get_or_404(ServiceTicket, ticket_id)
  if mechanic in service_ticket.mechanics:
    return jsonify({'message': 'Mechanic already assigned to ticket'}), 400
  service_ticket.mechanics.append(mechanic)
  db.session.commit()
  return service_ticket_schema.jsonify(service_ticket), 200


# Remove mechanic from service ticket
@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit('10 per minute')
def remove_mechanic(ticket_id, mechanic_id):
  mechanic = get_or_404(Mechanic, mechanic_id)
  service_ticket = get_or_404(ServiceTicket, ticket_id)
  if mechanic not in service_ticket.mechanics:
    return jsonify({'message': 'Mechanic not assigned to ticket'}), 400
  service_ticket.mechanics.remove(mechanic)
  db.session.commit()
  return service_ticket_schema.jsonify(service_ticket), 200
  

# Get all service tickets for all customers  
@service_tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_service_tickets():
  query = select(ServiceTicket).order_by(ServiceTicket.created_at.desc())
  service_tickets = paginate(query, service_tickets_schema)
  return jsonify(service_tickets['items']), 200


# Get service ticket by ticket ID
@service_tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@cache.cached(timeout=60)
def get_service_ticket(ticket_id):
  service_ticket = get_or_404(ServiceTicket, ticket_id)
  return service_ticket_schema.jsonify(service_ticket), 200


# Get all service tickets for a specific car of logged-in customer
@service_tickets_bp.route('/my-tickets/<int:car_num>', methods=['GET'])
@cache.cached(timeout=60)
@token_required
def get_customer_service_tickets(customer_id, car_num):
  customer = get_or_404(Customer, customer_id)
  if car_num < 1 or car_num > len(customer.cars):
    return jsonify({'message': 'Input valid car number'}), 400
  car = customer.cars[car_num - 1]
  query = (
    select(ServiceTicket)
    .where(ServiceTicket.car_vin == car.vin)
    .order_by(ServiceTicket.created_at.desc())
  )
  customer_service_tickets = paginate(query, service_tickets_schema)
  return jsonify(customer_service_tickets['items']), 200