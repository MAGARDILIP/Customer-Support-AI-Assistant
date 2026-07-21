"""
Order API Routes — Direct order lookup endpoints.
"""
from fastapi import APIRouter, HTTPException
from backend.database.connection import get_ecommerce_session
from backend.database.models import Order, Customer

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("/{order_number}")
async def get_order(order_number: str):
    """Get order details by order number."""
    session = get_ecommerce_session()
    try:
        order = (
            session.query(Order)
            .filter(Order.order_number == order_number.upper())
            .first()
        )
        if not order:
            raise HTTPException(status_code=404, detail=f"Order '{order_number}' not found.")
        return {"order": order.to_dict()}
    finally:
        session.close()


@router.get("/search/by-email")
async def search_by_email(email: str):
    """Search orders by customer email."""
    session = get_ecommerce_session()
    try:
        customer = session.query(Customer).filter(Customer.email == email.lower()).first()
        if not customer:
            raise HTTPException(status_code=404, detail=f"No customer found with email '{email}'.")
        orders = (
            session.query(Order)
            .filter(Order.customer_id == customer.id)
            .order_by(Order.order_date.desc())
            .all()
        )
        return {
            "customer": customer.to_dict(),
            "orders": [o.to_dict() for o in orders],
            "total_orders": len(orders),
        }
    finally:
        session.close()


@router.get("/search/by-phone")
async def search_by_phone(phone: str):
    """Search orders by customer phone number."""
    session = get_ecommerce_session()
    try:
        customers = (
            session.query(Customer)
            .filter(Customer.phone.contains(phone))
            .all()
        )
        if not customers:
            raise HTTPException(status_code=404, detail=f"No customer found with phone '{phone}'.")

        results = []
        for customer in customers:
            orders = (
                session.query(Order)
                .filter(Order.customer_id == customer.id)
                .order_by(Order.order_date.desc())
                .all()
            )
            results.append({
                "customer": customer.to_dict(),
                "orders": [o.to_dict() for o in orders],
            })
        return {"results": results}
    finally:
        session.close()


@router.get("/")
async def list_orders(limit: int = 20, offset: int = 0):
    """List all orders (paginated)."""
    session = get_ecommerce_session()
    try:
        orders = (
            session.query(Order)
            .order_by(Order.order_date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        total = session.query(Order).count()
        return {
            "orders": [o.to_dict() for o in orders],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        session.close()
