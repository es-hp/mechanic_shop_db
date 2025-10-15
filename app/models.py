from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Table, Column, DateTime, Integer, CheckConstraint, Numeric, func, select
from typing import List
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# Association Tables
service_ticket_mechanic = Table(
  "service_ticket_mechanic",
  Base.metadata,
  Column("service_ticket_id", ForeignKey("service_tickets.id"), primary_key=True),
  Column("mechanic_id", ForeignKey("mechanics.id"), primary_key=True)
)

# Models
@dataclass
class Customer(Base):
  __tablename__ = "customers"
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  phone: Mapped[str] = mapped_column(String(25), nullable=False)
  email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  cars: Mapped[List["Car"]] = relationship(
    back_populates="customer",
    cascade="all, delete-orphan"
  )

@dataclass
class Car(Base):
  __tablename__ = "cars"
  vin: Mapped[str] = mapped_column(String(17), primary_key=True)
  make: Mapped[str] = mapped_column(String(50))
  model: Mapped[str] = mapped_column(String(100))
  year: Mapped[int] = mapped_column(Integer, CheckConstraint("year BETWEEN 1000 AND 9999"))
  color: Mapped[str] = mapped_column(String(50))
  customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
  customer: Mapped["Customer"] = relationship(back_populates="cars")
  service_tickets: Mapped[List["ServiceTicket"]] = relationship(
    back_populates="car",
    cascade="all, delete-orphan"
  )
  
@dataclass
class ServiceTicket(Base):
  __tablename__ = "service_tickets"
  id: Mapped[int] = mapped_column(primary_key=True)
  service_desc: Mapped[str] = mapped_column(String(200), nullable=False)
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc)
  )
  car_vin: Mapped[str] = mapped_column(ForeignKey("cars.vin"))
  car: Mapped["Car"] = relationship(back_populates="service_tickets")
  mechanics: Mapped[List["Mechanic"]] = relationship(
    secondary=service_ticket_mechanic,
    back_populates="service_tickets"
  )
  @property
  def customer(self):
    return self.car.customer if self.car else None
  
@dataclass
class Mechanic(Base):
  __tablename__ = "mechanics"
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  phone: Mapped[str] = mapped_column(String(25), nullable=False)
  address: Mapped[str] = mapped_column(String(200), nullable=False)
  email: Mapped[str] = mapped_column(String(100))
  salary: Mapped[Decimal] = mapped_column(Numeric(10, 2))
  service_tickets: Mapped[List["ServiceTicket"]] = relationship(
    secondary=service_ticket_mechanic,
    back_populates="mechanics"
  )
  
  @classmethod
  def get_ticket_counts(cls):
    sub_query = (
      select(service_ticket_mechanic.c.mechanic_id,
      func.coalesce(func.count(ServiceTicket.id), 0).label('ticket_count')
      )
      .join(ServiceTicket, ServiceTicket.id == service_ticket_mechanic.c.service_ticket_id)
      .group_by(service_ticket_mechanic.c.mechanic_id)
      .subquery()
    )
    query = (
      select(cls, func.coalesce(sub_query.c.ticket_count, 0).label('ticket_count'))
      .outerjoin(sub_query, cls.id == sub_query.c.mechanic_id)
      .order_by(func.coalesce(sub_query.c.ticket_count, 0).desc())
    )
    results = db.session.execute(query).all()
    
    mechanics = []
    for mech, count in results:
      mech.ticket_count = count
      mechanics.append(mech)
    
    return query, mechanics