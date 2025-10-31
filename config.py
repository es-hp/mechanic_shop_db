import os
from dotenv import load_dotenv

load_dotenv()

class DevelopmentConfig:
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
  DEBUG = True
  
class TestingConfig:
  SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
  DEBUG = True
  CACHE_TYPE = 'SimpleCache'

class ProductionConfig:
  pass