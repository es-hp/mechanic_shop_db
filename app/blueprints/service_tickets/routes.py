from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ServiceTicket, db, Mechanic
from . import service_tickets_bp
from app.helpers import get_or_404, load_request_data


@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
  service_ticket_data = load_request_data(service_ticket_schema)
  new_service_ticket = ServiceTicket(**service_ticket_data)
  db.session.add(new_service_ticket)
  db.session.commit()
  return service_ticket_schema.jsonify(new_service_ticket), 201
  

@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
  mechanic = get_or_404(Mechanic, mechanic_id)
  service_ticket = get_or_404(ServiceTicket, ticket_id)
  if mechanic in service_ticket.mechanics:
    return jsonify({'message': 'Mechanic already assigned to ticket'}), 400
  service_ticket.mechanics.append(mechanic)
  db.session.commit()
  return service_ticket_schema.jsonify(service_ticket), 200


@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
  mechanic = get_or_404(Mechanic, mechanic_id)
  service_ticket = get_or_404(ServiceTicket, ticket_id)
  if mechanic not in service_ticket.mechanics:
    return jsonify({'message': 'Mechanic not assigned to ticket'}), 400
  service_ticket.mechanics.remove(mechanic)
  db.session.commit()
  return service_ticket_schema.jsonify(service_ticket), 200
  
  
@service_tickets_bp.route('/', methods=['GET'])
def get_service_tickets():
  query = select(ServiceTicket)
  service_tickets = db.session.execute(query).scalars().all()
  return service_tickets_schema.jsonify(service_tickets), 200


@service_tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def get_service_ticket(ticket_id):
  service_ticket = get_or_404(ServiceTicket, ticket_id)
  return service_ticket_schema.jsonify(service_ticket), 200
