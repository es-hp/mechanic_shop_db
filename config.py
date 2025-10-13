import os
from dotenv import load_dotenv

load_dotenv()

class DevelopmentConfig:
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
  DEBUG = True
  
class TestingConfig:
  pass

class ProductionConfig:
  pass