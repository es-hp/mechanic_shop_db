from .schemas import inventory_schema, inventories_schema, inventory_schema_dict
from flask import jsonify
from sqlalchemy import select
from app.models import db, Inventory
from . import inventory_bp
from app.utils.helpers import load_request_data, get_or_404, paginate, check_role
from app.utils.jwt_utils import token_required
from app.extensions import limiter, cache

@inventory_bp.route('/', methods=['POST'])
@limiter.limit('10 per minute')
@token_required
def create_inventory_item(user, role):
  check_role(role, 'mechanic')
  item = load_request_data(inventory_schema, Inventory)
  query = select(Inventory).where(Inventory.name == item.name)
  existing_item = db.session.execute(query).scalar_one_or_none()
  if existing_item:
    return jsonify({'message': f'This item already in the inventory: {item.name}'}), 409
  db.session.add(item)
  db.session.commit()
  return inventory_schema.jsonify(item), 201


@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=1)
@token_required
def get_inventory_items(user, role):
  check_role(role, 'mechanic')
  query = select(Inventory).order_by(Inventory.name)
  items = paginate(query, inventories_schema)
  return jsonify(items['items']), 200


@inventory_bp.route('/<int:id>', methods=['GET'])
@cache.cached(timeout=1)
@token_required
def get_inventory_item(user, role, id):
  check_role(role, 'mechanic')
  item = get_or_404(Inventory, id)
  return inventory_schema.jsonify(item), 200


@inventory_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit('5 per minute')
@token_required
def delete_inventory_item(user, role, id):
  check_role(role, 'mechanic')
  item = get_or_404(Inventory, id)
  db.session.delete(item)
  db.session.commit()
  return jsonify({"message": f"Successfully deleted item: {item.name}"}), 200
  