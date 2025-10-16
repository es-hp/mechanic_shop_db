from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Mechanic
    load_instance = True
  ticket_count = fields.Integer(dump_only=True)
  salary = fields.Float()
  password = fields.String(required=True, load_only=True)
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_schema_dict = MechanicSchema(load_instance=False)