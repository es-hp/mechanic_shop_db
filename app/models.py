from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Table, Column, DateTime, Integer, CheckConstraint, Float, func, select
from typing import List
from dataclasses import dataclass
from datetime import datetime, timezone


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)


# Association Tables
service_ticket_mechanic = Table(
  'service_ticket_mechanic',
  Base.metadata,
  Column('service_ticket_id', ForeignKey('service_tickets.id'), primary_key=True),
  Column('mechanic_id', ForeignKey('mechanics.id'), primary_key=True)
)


# Models
@dataclass
class Customer(Base):
  __tablename__ = 'customers'
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  phone: Mapped[str] = mapped_column(String(25), nullable=False)
  email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  cars: Mapped[List['Car']] = relationship(
    back_populates='customer',
    cascade='all, delete-orphan'
  )


@dataclass
class Car(Base):
  __tablename__ = 'cars'
  vin: Mapped[str] = mapped_column(String(17), primary_key=True)
  make: Mapped[str] = mapped_column(String(50))
  model: Mapped[str] = mapped_column(String(100))
  year: Mapped[int] = mapped_column(Integer, CheckConstraint('year BETWEEN 1000 AND 9999'))
  color: Mapped[str] = mapped_column(String(50))
  customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
  customer: Mapped['Customer'] = relationship(back_populates='cars')
  service_tickets: Mapped[List['ServiceTicket']] = relationship(
    back_populates='car',
    cascade='all, delete-orphan'
  )
  
  
@dataclass
class ServiceTicket(Base):
  __tablename__ = 'service_tickets'
  id: Mapped[int] = mapped_column(primary_key=True)
  service_desc: Mapped[str] = mapped_column(String(200), nullable=False)
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc)
  )
  car_vin: Mapped[str] = mapped_column(ForeignKey('cars.vin'))
  car: Mapped['Car'] = relationship(back_populates='service_tickets')
  mechanics: Mapped[List['Mechanic']] = relationship(
    secondary=service_ticket_mechanic,
    back_populates='service_tickets'
  )
  parts: Mapped[List['ServiceTicketInventory']] = relationship(
    back_populates='service_tickets',
    cascade='all, delete-orphan'
  )
  @property
  def customer(self):
    return self.car.customer if self.car else None
  

@dataclass
class Mechanic(Base):
  __tablename__ = 'mechanics'
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  phone: Mapped[str] = mapped_column(String(25), nullable=False)
  address: Mapped[str] = mapped_column(String(200), nullable=False)
  email: Mapped[str] = mapped_column(String(100), nullable=False)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  salary: Mapped[float] = mapped_column(Float(precision=2))
  service_tickets: Mapped[List['ServiceTicket']] = relationship(
    secondary=service_ticket_mechanic,
    back_populates='mechanics'
  )
  
  @classmethod
  def get_ticket_counts(cls):
    # sub_query: temporary table with mechanic_id, and ticket_count columns
    sub_query = (
      select(
        service_ticket_mechanic.c.mechanic_id,
        func.count(ServiceTicket.id).label('ticket_count')
      )
      .join(ServiceTicket, ServiceTicket.id == service_ticket_mechanic.c.service_ticket_id)
      .group_by(service_ticket_mechanic.c.mechanic_id)
      .subquery()
    )
    ticket_count_col = func.coalesce(sub_query.c.ticket_count, 0)
    base_query = (
      select(cls, ticket_count_col.label('ticket_count'))
      .outerjoin(sub_query, sub_query.c.mechanic_id == cls.id)
    )
    
    query = base_query.order_by(ticket_count_col.desc())
    
    results = db.session.execute(query).all()
    
    mechanics = []
    for mech, count in results:
      mech.ticket_count = count
      mechanics.append(mech)
    
    return query, mechanics, ticket_count_col, sub_query, base_query
  
  
@dataclass
class Inventory(Base):
  __tablename__ = 'inventory'
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  price: Mapped[float] = mapped_column(Float)
  service_tickets: Mapped[List['ServiceTicketInventory']] = relationship(
    back_populates='inventory',
    cascade='all, delete-orphan'
  )


class ServiceTicketInventory(Base):
  __tablename__ = 'service_ticket_inventory'
  service_ticket_id: Mapped[int] = mapped_column(
    ForeignKey('service_tickets.id'),
    primary_key=True
  )
  inventory_id: Mapped[int] = mapped_column(
    ForeignKey('inventory.id'),
    primary_key=True
  )
  quantity: Mapped[int] = mapped_column(Integer, nullable=False)
  
  service_tickets: Mapped['ServiceTicket'] = relationship(
    back_populates='parts'
  )
  inventory: Mapped['Inventory'] = relationship(back_populates='service_tickets')