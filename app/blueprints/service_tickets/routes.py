from .schemas import service_ticket_schema, service_tickets_schema, edit_ticket_mechs_schema, detailed_service_ticket_schema, detailed_service_tickets_schema
from flask import request, jsonify
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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



# Add and/or remove mechanic from service ticket
@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@limiter.limit('10 per minute')
def edit_ticket_mechanics(ticket_id):
  service_ticket = get_or_404(ServiceTicket, ticket_id)
  data = load_request_data(edit_ticket_mechs_schema)
  
  add_ids = data.get('add_mech_ids') or []
  remove_ids = data.get('remove_mech_ids') or []
  
  ## Filter list of ids from payload by checking with model if models with given ids exist
  def get_ids (model, id_list):
    return set(
      db.session.execute(select(model.id).where(model.id.in_(id_list))).scalars().all()
    ) if id_list else set()
  
  ## Create new lists with only valid ids
  ids_to_add = get_ids(Mechanic, add_ids)
  ids_to_remove = get_ids(Mechanic, remove_ids)
  
  ## Create list of all non-valid ids that were in payload and returns 'not found' message
  not_found_ids = [
    *[i for i in add_ids if i not in ids_to_add],
    *[i for i in remove_ids if i not in ids_to_remove]
  ]
  if not_found_ids:
    ids_string = ", ".join(map(str, not_found_ids))
    return jsonify({'message': f'Mechanic(s) not found for ID(s): {ids_string}'}), 404
  
  ## Create lists of mechanic objects from list of ids
  def get_objs (model, id_list):
    return list(
      db.session.execute(select(model).where(model.id.in_(id_list))).scalars().all()
    )
  
  ## Set error variables
  add_mech_error = None 
  remove_mech_error = None
  
  ## Add new mechanic to list if mechanic is not already in list
  mechs_to_add = get_objs(Mechanic, ids_to_add)
  existing_mechs = [mech for mech in service_ticket.mechanics]
  new_mechs = [mech for mech in mechs_to_add if mech not in existing_mechs]
  duplicate_mechs = [mech for mech in mechs_to_add if mech not in new_mechs]

  if duplicate_mechs:
    dup_mech_text = ", ".join([f'{mech.name} (ID: {mech.id})' for mech in duplicate_mechs])
    add_mech_error = {'message': f"Mechanic {dup_mech_text} {'is' if len(duplicate_mechs) == 1 else 'are'} already on this ticket."}
  if new_mechs:
    service_ticket.mechanics.extend(new_mechs)
    existing_mechs = list(service_ticket.mechanics)
    
  ## Remove mechanic from list if mechanic is on the list
  mechs_to_remove = get_objs(Mechanic, ids_to_remove)
  missing_mechs = [mech for mech in mechs_to_remove if mech not in existing_mechs]
  if missing_mechs:
    missing_mech_text = ", ".join([f'{mech.name} (ID: {mech.id})' for mech in missing_mechs])
    remove_mech_error = {'message': f"Mechanic {missing_mech_text} {'is' if len(missing_mechs) == 1 else 'are'} not on this ticket."}
  else:
    for mech in mechs_to_remove:
      service_ticket.mechanics.remove(mech)
  
  ## Return one or both error messages if error
  if add_mech_error and remove_mech_error:
    return jsonify({
      'add_error': add_mech_error['message'],
      'remove_error': remove_mech_error['message']
    }), 400
  elif add_mech_error:
    return jsonify(add_mech_error), 400
  elif remove_mech_error:
    return jsonify(remove_mech_error), 400
  
  db.session.commit()
  return detailed_service_ticket_schema.jsonify(service_ticket), 200
    

  
# # Add mechanic to service ticket
# @service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
# @limiter.limit('10 per minute')
# def assign_mechanic(ticket_id, mechanic_id):
#   mechanic = get_or_404(Mechanic, mechanic_id)
#   service_ticket = get_or_404(ServiceTicket, ticket_id)
#   if mechanic in service_ticket.mechanics:
#     return jsonify({'message': 'Mechanic already assigned to ticket'}), 400
#   service_ticket.mechanics.append(mechanic)
#   db.session.commit()
#   return detailed_service_ticket_schema.jsonify(service_ticket), 200


# # Remove mechanic from service ticket
# @service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
# @limiter.limit('10 per minute')
# def remove_mechanic(ticket_id, mechanic_id):
#   mechanic = get_or_404(Mechanic, mechanic_id)
#   service_ticket = get_or_404(ServiceTicket, ticket_id)
#   if mechanic not in service_ticket.mechanics:
#     return jsonify({'message': 'Mechanic not assigned to ticket'}), 400
#   service_ticket.mechanics.remove(mechanic)
#   db.session.commit()
#   return detailed_service_ticket_schema.jsonify(service_ticket), 200
  

# Get all service tickets for all customers  
@service_tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_service_tickets():
  query = select(ServiceTicket).order_by(ServiceTicket.created_at.desc())
  service_tickets = paginate(query, detailed_service_tickets_schema)
  return jsonify(service_tickets['items']), 200


# Get service ticket by ticket ID
@service_tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@cache.cached(timeout=60)
def get_service_ticket(ticket_id):
  service_ticket = get_or_404(ServiceTicket, ticket_id)
  return detailed_service_ticket_schema.jsonify(service_ticket), 200


# Get all service tickets for a specific car of logged-in customer
# Had to include car_num because I created an additional Car module that wasn't in the assignment
@service_tickets_bp.route('/my-tickets/<int:car_num>', methods=['GET'])
@cache.cached(timeout=60)
@token_required
def get_car_service_tickets(customer_id, car_num):
  customer = get_or_404(Customer, customer_id)
  if car_num < 1 or car_num > len(customer.cars):
    return jsonify({'message': 'Input valid car number'}), 400
  car = customer.cars[car_num - 1]
  query = (
    select(ServiceTicket)
    .where(ServiceTicket.car_vin == car.vin)
    .order_by(ServiceTicket.created_at.desc())
  )
  customer_car_tickets = paginate(query, service_tickets_schema)
  return jsonify(customer_car_tickets['items']), 200


# Figured out how to get all service tickets for a customer
@service_tickets_bp.route('/my-tickets', methods=['GET'])
@cache.cached(timeout=60)
@token_required
def get_customer_service_tickets(customer_id):
  customer = get_or_404(Customer, customer_id)
  if not customer.cars:
    return jsonify({'message': 'No cars associated with this account'})
  query = (
    select(ServiceTicket)
    .join(ServiceTicket.car)
    .join(Car.customer)
    .where(Customer.id == customer_id)
    .order_by(ServiceTicket.created_at.desc())
  )
  customer_tickets = paginate(query, service_tickets_schema)
  return jsonify(customer_tickets['items']), 200
  