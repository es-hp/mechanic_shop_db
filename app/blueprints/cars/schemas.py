from app.extensions import ma
from app.models import Car

class CarSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Car
    include_fk = True
    

car_schema = CarSchema()
cars_schema = CarSchema(many=True)