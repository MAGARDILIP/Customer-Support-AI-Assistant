"""
SQLAlchemy database models for the e-commerce mock data.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Customer(Base):
    """Customer table — stores customer information."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Product(Base):
    """Product table — stores product catalog."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    is_digital = Column(Boolean, default=False)

    # Relationships
    orders = relationship("Order", back_populates="product")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "description": self.description,
            "is_digital": self.is_digital,
        }


class Order(Base):
    """Order table — stores customer orders."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="Pending")
    order_date = Column(DateTime, nullable=False)
    delivery_date = Column(DateTime, nullable=True)
    tracking_number = Column(String(30), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    refund = relationship("Refund", back_populates="order", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else None,
            "customer_email": self.customer.email if self.customer else None,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "status": self.status,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "tracking_number": self.tracking_number,
            "is_digital": self.product.is_digital if self.product else False,
            "has_refund": self.refund is not None,
        }


class Refund(Base):
    """Refund table — stores refund requests."""
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="Pending")
    refund_amount = Column(Float, nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="refund")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "order_number": self.order.order_number if self.order else None,
            "reason": self.reason,
            "status": self.status,
            "refund_amount": self.refund_amount,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }


class ChatMessage(Base):
    """Chat history table — stores all conversation messages."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), nullable=False, index=True)
    role = Column(String(10), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_used = Column(String(50), nullable=True)
    tools_used = Column(JSON, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    language = Column(String(10), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "agent_used": self.agent_used,
            "tools_used": self.tools_used,
            "sentiment_score": self.sentiment_score,
            "language": self.language,
        }
