from app.extensions import ma
from app.models import Car, db
from marshmallow import fields

class CarSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Car
    include_fk = True
    load_instance = True
  service_tickets = fields.Pluck("ServiceTicketSchema", "id", many=True, dump_only=True)
    

car_schema = CarSchema(session=db.session)
cars_schema = CarSchema(many=True)
car_schema_dict = CarSchema(load_instance=False)