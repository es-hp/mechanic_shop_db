import unittest
from app import create_app
from app.models import db, Customer, Mechanic, Inventory, Car, ServiceTicket
from app.utils.jwt_utils import encode_token
from datetime import datetime, timezone

class TestInventory(unittest.TestCase):
  def setUp(self):
    self.app = create_app('TestingConfig')
    self.client = self.app.test_client()
    self.mechanic= Mechanic(
      name='test_mech',
      phone='555-555-6666',
      address='100 Main St. City, NY 00000',
      email='mech1@email.com',
      password='7890',
      salary=80000.0
    )
    self.customer = Customer(
      name='test_user',
      phone='555-111-2222',
      email='user@email.com',
      password='1234'      
    )
    self.car = Car(
      vin='80224526647584952',
      make='Honda',
      model='Civic',
      year=2020,
      color='Black',
      customer=self.customer
    )
    self.service_ticket = ServiceTicket(
      service_desc='Service A',
      car=self.car,
      created_at=datetime.now(timezone.utc)
    )
    self.inventory_item = Inventory(
      name='Tire',
      price=200.0
    )
    with self.app.app_context():
      db.drop_all()
      db.create_all()
      db.session.add_all([
        self.mechanic,
        self.customer,
        self.car,
        self.service_ticket,
        self.inventory_item
      ])
      db.session.commit()
      self.customer_token = encode_token(self.customer.id, 'customer')
      self.mechanic_token = encode_token(self.mechanic.id, 'mechanic')
      self.ticket_id = self.service_ticket.id
      self.mech_name = self.mechanic.name
      self.item_id = self.inventory_item.id
      self.item_name = self.inventory_item.name
  
  
  def auth_headers(self, role):
    token = getattr(self, f'{role}_token')
    return {'Authorization': f'Bearer {token}'}

  
  def test_create_inventory(self):
    item_payload = {
      'name': 'Battery',
      'price': 140.0      
    }
    response = self.client.post(
      '/inventory/',
      json=item_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.get_json()['name'], 'Battery')
    
    
  def test_conflict_creation(self):
    item_payload = {
      'name': 'Tire',
      'price': 200.0
    }
    response = self.client.post(
      '/inventory/',
      json=item_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 409)
    self.assertEqual(
      response.get_json()['message'],
      f'This item already in the inventory: {self.item_name}'
    )
    
  
  def test_get_inventory(self):
    response = self.client.get(
      '/inventory/',
        headers=self.auth_headers('mechanic')
      )
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response.get_json(), list)
    self.assertEqual(response.get_json()[0]['name'], 'Tire')

  
  def test_get_inventory_by_id(self):
    id = self.item_id
    response = self.client.get(
      f'/inventory/{id}',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['name'], self.item_name)


  def test_delete_inventory_by_id(self):
    id = self.item_id
    response = self.client.delete(
      f'/inventory/{id}',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      response.get_json()['message'],
      f'Successfully deleted item: {self.item_name}'
    )
  
  
  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()
      db.get_engine().dispose()


if __name__ == '__main__':
  unittest.main()