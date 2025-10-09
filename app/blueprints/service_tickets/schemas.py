from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields
    
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = ServiceTicket
    include_fk = True
  car_vin = fields.String(load_only=True)
  car = fields.Nested("CarSchema", dump_only=True)
  mechanics = fields.Pluck("MechanicSchema", "name", many=True, dump_only=True)
    

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)