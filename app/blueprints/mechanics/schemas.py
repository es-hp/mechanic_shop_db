from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Mechanic
    load_instance = True
  salary = fields.Float()
  ticket_count = fields.Integer(dump_only=True)
  service_tickets = fields.Pluck('ServiceTicketSchema', 'id', many=True, dump_only=True)
  password = fields.String(required=True, load_only=True)
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_schema_dict = MechanicSchema(load_instance=False)