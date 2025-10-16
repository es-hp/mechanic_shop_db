from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields
from ..cars.schemas import CarSchema
    
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = ServiceTicket
    include_fk = True
    load_instance = True
  car_vin = fields.String(load_only=True)
  car = fields.Nested(CarSchema(exclude=('service_tickets',)), dump_only=True)
  mechanics = fields.Pluck('MechanicSchema', 'name', many=True, dump_only=True)
  customer = fields.Nested('CustomerSchema', only=('id', 'name', 'phone'), dump_only=True)
    

service_ticket_schema = ServiceTicketSchema(exclude=('customer',))
service_tickets_schema = ServiceTicketSchema(exclude=('customer',), many=True)
detailed_service_ticket_schema = ServiceTicketSchema()
detailed_service_tickets_schema = ServiceTicketSchema(many=True)


class EditTicketMechsSchema(ma.Schema):
  add_mech_ids = fields.List(fields.Int())
  remove_mech_ids = fields.List(fields.Int())
  
edit_ticket_mechs_schema = EditTicketMechsSchema()