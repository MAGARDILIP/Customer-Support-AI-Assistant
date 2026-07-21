"""
Refund API Routes — Refund eligibility checking.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.database.connection import get_ecommerce_session
from backend.database.models import Order, Refund
from backend.config import settings
from datetime import datetime

router = APIRouter(prefix="/api/refunds", tags=["Refunds"])


class RefundCheckRequest(BaseModel):
    order_number: str


@router.post("/check")
async def check_refund_eligibility(request: RefundCheckRequest):
    """Check if an order is eligible for a refund."""
    session = get_ecommerce_session()
    try:
        order = (
            session.query(Order)
            .filter(Order.order_number == request.order_number.upper())
            .first()
        )
        if not order:
            raise HTTPException(status_code=404, detail=f"Order '{request.order_number}' not found.")

        # Run eligibility checks
        eligible = True
        reasons = []

        # Check existing refund
        existing = session.query(Refund).filter(Refund.order_id == order.id).first()
        if existing:
            return {
                "eligible": False,
                "order": order.to_dict(),
                "reason": f"Refund already {existing.status.lower()} for this order.",
                "existing_refund": existing.to_dict(),
            }

        # Check order status
        if order.status != "Delivered":
            eligible = False
            reasons.append(f"Order status is '{order.status}'. Only delivered orders can be refunded.")

        # Check digital product
        if order.product and order.product.is_digital:
            eligible = False
            reasons.append("Digital products are non-refundable.")

        # Check return window
        if order.delivery_date:
            days = (datetime.utcnow() - order.delivery_date).days
            if days > settings.REFUND_WINDOW_DAYS:
                eligible = False
                reasons.append(f"Return window expired ({days} days since delivery, limit is {settings.REFUND_WINDOW_DAYS}).")

        return {
            "eligible": eligible,
            "order": order.to_dict(),
            "refund_amount": order.total_price if eligible else 0,
            "reasons": reasons if not eligible else ["Order meets all refund requirements."],
        }
    finally:
        session.close()
