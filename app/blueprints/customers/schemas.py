from app.extensions import ma
from app.models import Customer
from marshmallow import fields
from ..cars.schemas import CarSchema

class CustomerSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Customer
    load_instance = True
  cars = fields.Nested(CarSchema, many=True)
  password = fields.String(required=True, load_only=True)
    
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_schema_dict = CustomerSchema(load_instance=False)