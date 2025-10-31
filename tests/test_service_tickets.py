import unittest
from app import create_app
from app.models import db, Customer, Mechanic, ServiceTicket, Car, Inventory
from app.utils.jwt_utils import encode_token
from datetime import datetime, timezone

class TestServiceTickets(unittest.TestCase):
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

  
  def test_create_ticket(self):
    ticket_payload = {
      'service_desc': 'Service B',
      'car_vin': '80224526647584952'
    }
    response = self.client.post(
      '/service_tickets/',
      json=ticket_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.get_json()['service_desc'], 'Service B')


  def test_not_found_creation(self):
    ticket_payload = {
      'service_desc': 'Service C',
      'car_vin': '12345678901234567'
    }
    response = self.client.post(
      '/service_tickets/',
      json=ticket_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 404)
    self.assertEqual(response.get_json()['message'], 'Car not found')

  
  def test_add_remove_mechanic(self):
    ticket_id = self.ticket_id
    add_remove_payload = {
      'add_mech_ids': [1],
      'remove_mech_ids': []
    }
    response = self.client.put(
      f'/service_tickets/{ticket_id}/edit',
      json=add_remove_payload,
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['mechanics'], [self.mech_name])

  
  def test_get_all_tickets(self):
    response = self.client.get(
      '/service_tickets/',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response.get_json(), list)

  
  def test_get_ticket(self):
    ticket_id = self.ticket_id
    response = self.client.get(
      f'/service_tickets/{ticket_id}',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json()['id'], 1)
  
  
  def test_get_ticket_by_customer(self):
    response = self.client.get(
      '/service_tickets/by-account',
      query_string={'id': 1},
      headers=self.auth_headers('mechanic')
    )
    first_ticket = response.get_json()[0]
    
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response.get_json(), list)
    self.assertEqual(
      first_ticket['service_desc'],
      'Service A'
    )

    
  def test_ticket_add_item(self):
    ticket_id = self.ticket_id
    item_id = self.item_id
    item_name = self.item_name
    count = 4
    response = self.client.patch(
      f'/service_tickets/{ticket_id}/add-item/{item_id}/count/{count}',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
      response.get_json()['message'],
      f"{item_name} added to service ticket {ticket_id}. {item_name}'s current quantity: {count}"
    )


  def test_ticket_remove_item(self):
    ticket_id = self.ticket_id
    item_id = self.item_id
    item_name = self.item_name
    count = 4
    
    add_response = self.client.patch(
      f'/service_tickets/{ticket_id}/add-item/{item_id}/count/{count}',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(add_response.status_code, 200)
    
    remove_response = self.client.patch(
      f'/service_tickets/{ticket_id}/remove-item/{item_id}',
      headers=self.auth_headers('mechanic')
    )
    self.assertEqual(remove_response.status_code, 200)
    self.assertEqual(
      remove_response.get_json()['message'],
      f"{item_name} removed from service ticket {ticket_id}. {item_name}'s current quantity: {count - 1}"
    )
  
  
  def tearDown(self):
    with self.app.app_context():
      db.session.remove()
      db.drop_all()
      db.get_engine().dispose()


if __name__ == '__main__':
  unittest.main()