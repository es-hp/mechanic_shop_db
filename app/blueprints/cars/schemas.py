from app.extensions import ma
from app.models import Car
from marshmallow import fields

class CarSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Car
    include_fk = True
  service_tickets = fields.Pluck("ServiceTicketSchema", "id", many=True, dump_only=True)
    

car_schema = CarSchema()
cars_schema = CarSchema(many=True)