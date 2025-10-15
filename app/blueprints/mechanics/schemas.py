from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Mechanic
  ticket_count = fields.Integer(dump_only=True)
  salary = fields.Decimal(places=2)
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)