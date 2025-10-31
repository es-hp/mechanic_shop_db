import unittest
from app import create_app
from app.models import db, Customer, Mechanic
from app.utils.jwt_utils import encode_token

class TestCustomers(unittest.TestCase):
  def setUp(self):
    self.app = create_app('TestingConfig')
    self.client = self.app.test_client()
    self.customer1 = Customer(
      name='test_user1',
      phone='555-111-2222',
      email='user1@email.com',
      password='1234'      
    )
    self.customer2 = Customer(
      name='test_user2',
      phone='555-333-4444',
      email='user2@email.com',
      password='1234'      
    )
    self.mechanic = Mechanic(
      name='test_mech',
      phone='555-555-6666',
      address='100 Main St. City, NY 00000',
      email='mech@email.com',
      password='7890',
      salary=80000.0
    )
    with self.app.app_context():
      db.drop_all()
      db.create_all()
      db.session.add_all([
        self.customer1,
        self.customer2,
        self.mechanic
      ])
      db.session.commit()
      self.customer_token = encode_token(self.customer1.id, 'customer')
      self.mechanic_token = encode_token(self.mechanic.id, 'mechanic')
  
  
  def auth_headers(self, role):
    token = getattr(self, f'{role}_token')
    return {'Authorization': f'Bearer {token}'}

  
  def test_create_customer(self):
    customer_payload = {
      'name': 'Helen Park',
      'phone': '555-111-2222',
      'email': 'helen@mail.com',
      'password': '1234'
    }
    response = self.client.post('/customers/', json=customer_payload)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.get_json()['name'], 'Helen Park')
    
    
  def test_invalid_creation(self):
    customer_payload = {
      'name': 'Helen Park',
      'phone': '555-111-2222',
      'password': '1234'
    }
    response = self.client.post('/customers/', json=customer_payload)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(
      response.get_json()['message']['email'],
      ['Missing data for required field.']
    )
    self.assertEqual(response.get_json()['error'], 'Bad Request')
    self.assertEqual(response.get_json()['code'], 400)
    
  
  def test_login_customer(self):
    credentials = {
      'email': 'user1@email.com',
      'password': '1234'
    }
    response = self.client.post('/customers/login', json=credentials)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['status'], 'success')
  
  
  def test_invalid_login(self):
    credentials = {
      'email': 'user1@email.com',
      'password': 'test'
    }
    response = self.client.post('/customers/login', json=credentials)
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response.get_json()['message'], 'Incorrect email or password')

  
  def test_get_all_customers(self):
    response = self.client.get(
      '/customers/',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response.get_json(), list)

  
  def test_get_customer(self):
    response = self.client.get(
      '/customers/account',
      query_string={'customer_id': 1},
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['name'], 'test_user1')
  
  
  def test_patch_customer(self):
    new_phone = {'phone': '555-888-9999'}
    response = self.client.patch(
      '/customers/',
      json=new_phone,
      headers=self.auth_headers('customer')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['phone'], '555-888-9999')


  def test_delete_customer(self):
    response = self.client.delete(
      '/customers/',
      headers=self.auth_headers('customer')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      response.get_json()['message'],
      'Successfully deleted your account.'
    )
  
  
  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()
      db.get_engine().dispose()


if __name__ == '__main__':
  unittest.main()