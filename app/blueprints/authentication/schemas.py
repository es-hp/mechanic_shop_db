from app.extensions import ma
from marshmallow import fields


class LoginSchema(ma.Schema):
  email = fields.Email(required=True)
  password = fields.String(required=True, load_only=True)
  
login_schema = LoginSchema()