from flask import Flask
from .extensions import ma
from .models import db
from .blueprints.customers import customers_bp
from .blueprints.cars import cars_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp
from werkzeug.exceptions import HTTPException
from .helpers import handle_http_exception

def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(f"config.{config_name}")
  
  # Initialize extensions
  ma.init_app(app)
  db.init_app(app)
  
  # Register blueprints
  app.register_blueprint(customers_bp, url_prefix="/customers")
  app.register_blueprint(cars_bp, url_prefix="/cars")
  app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
  app.register_blueprint(service_tickets_bp, url_prefix="/service_tickets")
  
  # Global error handler
  app.register_error_handler(HTTPException, handle_http_exception)

  
  return app