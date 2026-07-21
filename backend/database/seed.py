"""
Seed the e-commerce database with realistic mock data using Faker.
Generates customers, products, orders, and refund records.
"""
import random
import logging
from datetime import datetime, timedelta
from faker import Faker
from backend.database.connection import get_ecommerce_session, init_databases
from backend.database.models import Customer, Product, Order, Refund

logger = logging.getLogger(__name__)
fake = Faker()
Faker.seed(42)
random.seed(42)


# --- Product catalog with realistic e-commerce items ---
PRODUCT_CATALOG = [
    {"name": "Wireless Bluetooth Headphones", "category": "Electronics", "price": 79.99, "is_digital": False, "description": "Premium noise-cancelling over-ear headphones with 30-hour battery life."},
    {"name": "Organic Cotton T-Shirt", "category": "Clothing", "price": 24.99, "is_digital": False, "description": "100% organic cotton, available in multiple colors. Machine washable."},
    {"name": "Stainless Steel Water Bottle", "category": "Home & Kitchen", "price": 19.99, "is_digital": False, "description": "Double-wall insulated, keeps drinks cold 24h or hot 12h. 750ml capacity."},
    {"name": "Python Programming eBook", "category": "Digital", "price": 29.99, "is_digital": True, "description": "Comprehensive guide to Python programming. PDF format, instant delivery."},
    {"name": "Yoga Mat Premium", "category": "Sports", "price": 45.99, "is_digital": False, "description": "Non-slip, eco-friendly TPE material. 6mm thickness. Includes carry strap."},
    {"name": "Smart Watch Fitness Tracker", "category": "Electronics", "price": 149.99, "is_digital": False, "description": "Heart rate monitor, GPS, sleep tracking, 7-day battery life."},
    {"name": "Ceramic Coffee Mug Set", "category": "Home & Kitchen", "price": 34.99, "is_digital": False, "description": "Set of 4 handcrafted ceramic mugs. Microwave and dishwasher safe."},
    {"name": "Online Cooking Course", "category": "Digital", "price": 49.99, "is_digital": True, "description": "12-week online cooking masterclass with video lessons. Lifetime access."},
    {"name": "Leather Wallet", "category": "Accessories", "price": 39.99, "is_digital": False, "description": "Genuine leather bifold wallet with RFID blocking. Multiple card slots."},
    {"name": "Running Shoes", "category": "Sports", "price": 89.99, "is_digital": False, "description": "Lightweight mesh upper with responsive cushioning. Available in sizes 6-13."},
    {"name": "Portable Bluetooth Speaker", "category": "Electronics", "price": 59.99, "is_digital": False, "description": "Waterproof IPX7, 12-hour playtime, 360-degree sound."},
    {"name": "Organic Green Tea Pack", "category": "Food & Beverages", "price": 15.99, "is_digital": False, "description": "Premium Japanese green tea, 50 individually wrapped bags."},
    {"name": "Data Science Bootcamp", "category": "Digital", "price": 199.99, "is_digital": True, "description": "Complete data science curriculum with certificates. 6-month access."},
    {"name": "Kids Drawing Tablet", "category": "Electronics", "price": 69.99, "is_digital": False, "description": "10-inch LCD writing tablet for kids. Includes stylus pen."},
    {"name": "Bamboo Cutting Board Set", "category": "Home & Kitchen", "price": 28.99, "is_digital": False, "description": "Set of 3 organic bamboo cutting boards in different sizes."},
    {"name": "Wireless Mouse", "category": "Electronics", "price": 22.99, "is_digital": False, "description": "Ergonomic design, silent click, 2.4GHz wireless. USB receiver included."},
    {"name": "Cotton Bed Sheet Set", "category": "Home & Kitchen", "price": 54.99, "is_digital": False, "description": "400-thread count Egyptian cotton. Queen size. Includes 2 pillowcases."},
    {"name": "Photography Masterclass", "category": "Digital", "price": 79.99, "is_digital": True, "description": "Professional photography course. 8 modules, 40+ hours of video content."},
    {"name": "Stainless Steel Cookware Set", "category": "Home & Kitchen", "price": 129.99, "is_digital": False, "description": "10-piece professional cookware set. Induction compatible."},
    {"name": "Backpack Travel Bag", "category": "Accessories", "price": 64.99, "is_digital": False, "description": "40L capacity, laptop compartment, water-resistant. TSA-friendly design."},
    {"name": "Resistance Bands Set", "category": "Sports", "price": 18.99, "is_digital": False, "description": "Set of 5 bands with different resistance levels. Includes door anchor."},
    {"name": "Scented Candle Collection", "category": "Home & Kitchen", "price": 32.99, "is_digital": False, "description": "Set of 6 soy wax candles. Lavender, vanilla, ocean, and more. 40-hour burn."},
    {"name": "USB-C Hub Adapter", "category": "Electronics", "price": 34.99, "is_digital": False, "description": "7-in-1 adapter: HDMI, USB 3.0, SD/TF card reader, PD charging."},
    {"name": "Kids Educational Game App", "category": "Digital", "price": 9.99, "is_digital": True, "description": "Interactive learning app for ages 3-8. Math, reading, and science."},
    {"name": "Denim Jacket", "category": "Clothing", "price": 59.99, "is_digital": False, "description": "Classic fit denim jacket. Premium cotton denim. Multiple sizes available."},
    {"name": "Electric Toothbrush", "category": "Personal Care", "price": 44.99, "is_digital": False, "description": "Sonic technology, 5 brushing modes, 2-minute timer. Includes 3 brush heads."},
    {"name": "Protein Powder Vanilla", "category": "Food & Beverages", "price": 38.99, "is_digital": False, "description": "Whey protein isolate, 25g per serving. No artificial sweeteners. 2lb tub."},
    {"name": "Desk Organizer Set", "category": "Office", "price": 26.99, "is_digital": False, "description": "Wooden desk organizer with pen holder, phone stand, and memo tray."},
    {"name": "Wireless Earbuds", "category": "Electronics", "price": 49.99, "is_digital": False, "description": "True wireless earbuds with active noise cancellation. 6-hour battery."},
    {"name": "Gardening Tool Set", "category": "Home & Kitchen", "price": 42.99, "is_digital": False, "description": "8-piece stainless steel garden tools with ergonomic handles and storage bag."},
]

ORDER_STATUSES = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
REFUND_REASONS = [
    "Item arrived damaged",
    "Wrong item received",
    "Item not as described",
    "Changed my mind",
    "Item doesn't fit",
    "Quality not as expected",
    "Ordered by mistake",
]


def seed_customers(session, count: int = 20) -> list[Customer]:
    """Generate mock customers."""
    customers = []
    for _ in range(count):
        customer = Customer(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.phone_number()[:15],
            address=fake.address(),
            created_at=fake.date_time_between(start_date="-1y", end_date="now"),
        )
        customers.append(customer)
    session.add_all(customers)
    session.commit()
    logger.info(f"Seeded {count} customers.")
    return customers


def seed_products(session) -> list[Product]:
    """Load products from the catalog."""
    products = []
    for item in PRODUCT_CATALOG:
        product = Product(**item)
        products.append(product)
    session.add_all(products)
    session.commit()
    logger.info(f"Seeded {len(products)} products.")
    return products


def seed_orders(session, customers: list, products: list, count: int = 80) -> list[Order]:
    """Generate mock orders with realistic statuses and dates."""
    orders = []
    for i in range(count):
        customer = random.choice(customers)
        product = random.choice(products)
        quantity = random.randint(1, 3)
        order_date = fake.date_time_between(start_date="-90d", end_date="now")
        status = random.choices(
            ORDER_STATUSES,
            weights=[10, 10, 15, 55, 10],  # Most orders are delivered
            k=1,
        )[0]

        delivery_date = None
        tracking_number = None
        if status in ("Shipped", "Delivered"):
            tracking_number = f"TRK{fake.bothify(text='??########').upper()}"
        if status == "Delivered":
            delivery_date = order_date + timedelta(days=random.randint(2, 10))
        elif status == "Shipped":
            delivery_date = order_date + timedelta(days=random.randint(5, 15))

        order = Order(
            order_number=f"ORD-{1000 + i}",
            customer_id=customer.id,
            product_id=product.id,
            quantity=quantity,
            total_price=round(product.price * quantity, 2),
            status=status,
            order_date=order_date,
            delivery_date=delivery_date,
            tracking_number=tracking_number,
        )
        orders.append(order)
    session.add_all(orders)
    session.commit()
    logger.info(f"Seeded {count} orders.")
    return orders


def seed_refunds(session, orders: list, count: int = 15) -> list[Refund]:
    """Generate mock refund records for some delivered orders."""
    delivered_orders = [o for o in orders if o.status == "Delivered"]
    refund_orders = random.sample(delivered_orders, min(count, len(delivered_orders)))

    refunds = []
    for order in refund_orders:
        refund = Refund(
            order_id=order.id,
            reason=random.choice(REFUND_REASONS),
            status=random.choice(["Pending", "Approved", "Rejected"]),
            refund_amount=order.total_price,
            requested_at=order.delivery_date + timedelta(days=random.randint(1, 20))
            if order.delivery_date
            else datetime.utcnow(),
            processed_at=None,
        )
        if refund.status in ("Approved", "Rejected"):
            refund.processed_at = refund.requested_at + timedelta(days=random.randint(1, 5))
        refunds.append(refund)

    session.add_all(refunds)
    session.commit()
    logger.info(f"Seeded {len(refunds)} refunds.")
    return refunds


def seed_database():
    """Run the full database seed process."""
    session = get_ecommerce_session()
    try:
        # Check if already seeded
        existing = session.query(Customer).count()
        if existing > 0:
            logger.info(f"Database already seeded ({existing} customers). Skipping.")
            return

        logger.info("Seeding database with mock e-commerce data...")
        customers = seed_customers(session)
        products = seed_products(session)
        orders = seed_orders(session, customers, products)
        seed_refunds(session, orders)
        logger.info("Database seeding complete!")

    except Exception as e:
        session.rollback()
        logger.error(f"Database seeding failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_databases()
    seed_database()
