from app.extensions import ma
from app.models import Inventory
from marshmallow import fields

class InventorySchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Inventory
    load_instance = True
  price = fields.Float()
    
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
inventory_schema_dict = InventorySchema(load_instance=False)