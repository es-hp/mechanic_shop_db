import os
from dotenv import load_dotenv

load_dotenv()

class DevelopmentConfig:
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
  DEBUG = True
  
class TestingConfig:
  SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
  DEBUG = True
  CACHE_TYPE = 'SimpleCache'

class ProductionConfig:
  SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
  CACHE_TYPE = 'SimpleCache'