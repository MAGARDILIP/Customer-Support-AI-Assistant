"""
Order Lookup Tool — Searches orders by number, email, or phone.
"""
import logging
from backend.database.connection import get_ecommerce_session
from backend.database.models import Order, Customer

logger = logging.getLogger(__name__)


def order_lookup_fn(query: str) -> str:
    """
    Look up order information by order number, email, or phone.
    Returns formatted order details.
    """
    session = get_ecommerce_session()
    try:
        query = query.strip()

        # Try order number
        if query.upper().startswith("ORD-"):
            order = session.query(Order).filter(Order.order_number == query.upper()).first()
            if order:
                data = order.to_dict()
                return (
                    f"Order Found:\n"
                    f"  Order Number: {data['order_number']}\n"
                    f"  Status: {data['status']}\n"
                    f"  Product: {data.get('product_name', 'N/A')}\n"
                    f"  Quantity: {data.get('quantity', 0)}\n"
                    f"  Total: ${data.get('total_price', 0):.2f}\n"
                    f"  Order Date: {data.get('order_date', 'N/A')}\n"
                    f"  Delivery Date: {data.get('delivery_date', 'N/A')}\n"
                    f"  Tracking: {data.get('tracking_number', 'N/A')}\n"
                    f"  Address: {data.get('shipping_address', 'N/A')}"
                )
            return f"No order found with number '{query}'."

        # Try email
        if "@" in query:
            customer = session.query(Customer).filter(Customer.email == query.lower()).first()
            if customer:
                orders = session.query(Order).filter(Order.customer_id == customer.id).all()
                if orders:
                    result = f"Found {len(orders)} orders for {customer.name} ({query}):\n"
                    for o in orders[:5]:
                        result += f"  - {o.order_number}: {o.status} | ${o.total_price:.2f}\n"
                    return result
            return f"No customer found with email '{query}'."

        return f"Could not parse query '{query}'. Use an order number (ORD-XXXX) or email."

    except Exception as e:
        logger.error(f"Order lookup failed: {e}")
        return f"Error looking up order: {str(e)}"
    finally:
        session.close()
