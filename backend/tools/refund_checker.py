"""
Refund Eligibility Checker Tool — Validates refund rules.
"""
import logging
from datetime import datetime
from backend.database.connection import get_ecommerce_session
from backend.database.models import Order, Refund
from backend.config import settings

logger = logging.getLogger(__name__)


def refund_check_fn(order_number: str) -> str:
    """
    Check if an order is eligible for a refund based on business rules.
    Rules: 30-day window, must be delivered, no digital products, no existing refund.
    """
    session = get_ecommerce_session()
    try:
        order = session.query(Order).filter(Order.order_number == order_number.upper()).first()
        if not order:
            return f"Order '{order_number}' not found."

        issues = []

        # Check existing refund
        existing = session.query(Refund).filter(Refund.order_id == order.id).first()
        if existing:
            return f"Refund already {existing.status.lower()} for order {order_number}. Amount: ${existing.refund_amount:.2f}"

        # Check order status
        if order.status != "Delivered":
            issues.append(f"Order status is '{order.status}' — only delivered orders can be refunded.")

        # Check digital product
        if order.product and order.product.is_digital:
            issues.append("Digital products are non-refundable.")

        # Check return window
        if order.delivery_date:
            days = (datetime.utcnow() - order.delivery_date).days
            if days > settings.REFUND_WINDOW_DAYS:
                issues.append(f"Return window expired ({days} days since delivery, limit is {settings.REFUND_WINDOW_DAYS} days).")

        if issues:
            return f"NOT ELIGIBLE for refund:\n" + "\n".join(f"  - {i}" for i in issues)
        else:
            return (
                f"ELIGIBLE for refund!\n"
                f"  Order: {order_number}\n"
                f"  Refund Amount: ${order.total_price:.2f}\n"
                f"  Customer should return the item in original packaging."
            )

    except Exception as e:
        logger.error(f"Refund check failed: {e}")
        return f"Error checking refund: {str(e)}"
    finally:
        session.close()
