import unittest
from app import create_app
from app.models import db, Customer, Mechanic
from app.utils.jwt_utils import encode_token

class TestMechanics(unittest.TestCase):
  def setUp(self):
    self.app = create_app('TestingConfig')
    self.client = self.app.test_client()
    self.mechanic1= Mechanic(
      name='test_mech1',
      phone='555-555-6666',
      address='100 Main St. City, NY 00000',
      email='mech1@email.com',
      password='7890',
      salary=80000.0
    )
    self.mechanic2= Mechanic(
      name='test_mech2',
      phone='555-777-8888',
      address='200 Main St. City, NY 00000',
      email='mech2@email.com',
      password='4567',
      salary=80000.0
    )
    self.customer = Customer(
      name='test_user',
      phone='555-111-2222',
      email='user@email.com',
      password='1234'      
    )
    with self.app.app_context():
      db.drop_all()
      db.create_all()
      db.session.add_all([
        self.mechanic1,
        self.mechanic2,
        self.customer
      ])
      db.session.commit()
      self.customer_token = encode_token(self.customer.id, 'customer')
      self.mechanic_token = encode_token(self.mechanic1.id, 'mechanic')
  
  
  def auth_headers(self, role):
    token = getattr(self, f'{role}_token')
    return {'Authorization': f'Bearer {token}'}

  
  def test_create_mechanic(self):
    mechanic_payload = {
      'name': 'Helen Park',
      'phone': '555-111-2222',
      'address': '300 Main St. City, NY 00000',
      'email': 'helen@mail.com',
      'password': '1234',
      'salary': 75000.0
    }
    response = self.client.post(
      '/mechanics/',
      json=mechanic_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.get_json()['name'], 'Helen Park')
    
    
  def test_conflict_creation(self):
    mechanic_payload = {
      'name': 'Helen Park',
      'phone': '555-111-2222',
      'address': '300 Main St. City, NY 00000',
      'email': 'mech1@email.com',
      'password': '1234',
      'salary': 75000.0
    }
    response = self.client.post(
      '/mechanics/',
      json=mechanic_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 409)
    self.assertEqual(
      response.get_json()['message'],
      'A mechanic with this email already exists.'
    )
    
  
  def test_login_mechanic(self):
    credentials = {
      'email': 'mech1@email.com',
      'password': '7890'
    }
    response = self.client.post('/mechanics/login', json=credentials)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['status'], 'success')

  
  def test_get_all_mechanics(self):
    response = self.client.get(
      '/mechanics/',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response.get_json(), list)

  
  def test_get_mechanic(self):
    response = self.client.get(
      '/mechanics/my-account',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['phone'], '555-555-6666')
  
  
  def test_put_mechanic(self):
    mechanic_payload = {
      'name': 'test_mech1',
      'phone': '555-555-6666',
      'address': '100 Main St. City, NY 00000',
      'email': 'mech1@email.com',
      'password': '7890',
      'salary': 90000.0
    }
    response = self.client.put(
      '/mechanics/my-account',
      json=mechanic_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['salary'], 90000.0)

    
  def test_invalid_put(self):
    mechanic_payload = {
      'name': 'test_mech1',
      'phone': '555-555-6666',
      'email': 'mech1@email.com',
      'password': '7890',
      'salary': 90000.0
    }
    response = self.client.put(
      '/mechanics/my-account',
      json=mechanic_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 400)
    self.assertEqual(
      response.get_json()['message']['address'],
      ['Missing data for required field.']
    )


  def test_delete_mechanic(self):
    response = self.client.delete(
      '/mechanics/my-account',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      response.get_json()['message'],
      'Successfully deleted mechanic'
    )
  
  
  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()
      db.get_engine().dispose()


if __name__ == '__main__':
  unittest.main()