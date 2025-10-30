from flask import Flask
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.customers import customers_bp
from .blueprints.cars import cars_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp
from .blueprints.inventory import inventory_bp
from werkzeug.exceptions import HTTPException
from .utils.helpers import handle_http_exception
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
import os

load_dotenv()
SWAGGER_URL = os.getenv('SWAGGER_URL', '/api/docs')
API_URL = os.getenv('API_URL', '/static/swagger.yaml')

swaggerui_blueprint = get_swaggerui_blueprint(
  SWAGGER_URL,
  API_URL,
  config = {
    'app_name': 'Mechanic Shop API'
  }
)

def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(f'config.{config_name}')
  
  # Initialize extensions
  ma.init_app(app)
  db.init_app(app)
  limiter.init_app(app)
  cache.init_app(app)
  
  # Register blueprints
  app.register_blueprint(customers_bp, url_prefix='/customers')
  app.register_blueprint(cars_bp, url_prefix='/cars')
  app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
  app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')
  app.register_blueprint(inventory_bp, url_prefix='/inventory')
  app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
  
  # Global error handler
  app.register_error_handler(HTTPException, handle_http_exception)

  
  return app